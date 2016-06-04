import sys, re, difflib
import variables as v
from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLQuery import queryXofY, queryGetTypes, URITitle, getRedirectPage

# Find all properties that the given URI has
def findProperties(URI):
	query = """
	SELECT ?property
	WHERE {<%s> ?property ?value  }
	""" % (URI)

	sparql = SPARQLWrapper("http://nl.dbpedia.org/sparql")
	sparql.setQuery(query)
	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()

	raw_properties = []

	for result in results["results"]["bindings"]:
		for arg in result :
			answer = result[arg]["value"]
			raw_properties.append(answer)

	#below is also the "andersom" properties
	query = """
	SELECT DISTINCT ?prop   WHERE{
    ?page ?prop <%s>
    }
	""" % (URI)

	sparql.setQuery(query)
	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()

	for result in results["results"]["bindings"]:
		for arg in result :
			answer = result[arg]["value"]
			raw_properties.append(answer)

	#end of andersom properties

	properties = []
	for element in raw_properties:
		if "nl.dbpedia.org/property" in element:
			element = element.split("/")
			properties.append(element[-1])

	


	return list(set(properties))

#give alpino node and wordtype you want to extract see variables
def getTreeWordList(xml, wordtype):
	#appends the value of the word-attribute for all nodes that are dominated by the node 'xml'
	#that is the argument of the function, and returns this a single string
	leaves = xml.xpath('descendant-or-self::node[@word]')
	words = []
	for l in leaves :
		words.append(l.attrib[wordtype])
	return " ".join(words)

#Removes articles from the input
def removeArticles(input):
	articles = ["de", "het", "een"]
	for word in articles:
		if word in input:
			input = input.replace(word+" ", "")
	return input

#returns substring from input between the first found first and last strings
def findBetween( input, first, last ):
	try:
		start = input.index( first ) + len( first )
		end = input.index( last, start )
		return input[start:end]
	except ValueError:
		return ""

#Searches the given file on the given query
def search(query, file):
	outList = []
	for line in open(file, "r"):
		if re.search("^"+query, line , re.IGNORECASE):
			outList.append(line)
	return outList

#gives the URI of a given domain
def getDomainURI(concept):
	max = 0
	URI = None
	words = None
	for line in open("pairCounts", 'r'):
		if re.search("^"+concept, line, re.IGNORECASE): #search concept in pairCounts
			line = line.rstrip()
			line = line.split("\t") #split lines by tabs to separate elements
			if int(line[2])>max: #if occurcences is higher than the maximum found until now:
				max = int(line[2]) #new maximum amount of occurences
				URI = line[1] #store URI
	return URI

#Removes everything from string except numbers and letters
def makeAZ(string):
	return re.sub(r'[\W_]+', '', string)

# get similar properties to prop
def getSimilarProperties(prop, allProperties):
	return difflib.get_close_matches(prop, allProperties)

# Get all properties which are similiar to a synonym of prop
def getAllSimilarProperties(prop, allProperties):
	outList = []
	sw = getSimilarWords(prop)
	for word in sw:
		if word is not "":
			outList += getSimilarProperties(word, allProperties)
	outList += sw
	return outList

#search fot similar words
def getSimilarWords(string):
	returnList = []
	searchList = search(string, v.FILE_SYNONYMS)
	for item in searchList:
		returnList += item.split("#")
	if not returnList:
		returnList.append(string)
	return returnList

#Unknown how this worked
def findPropertySimilarWords(sentence):
	bestProp = None
	for verb in verbs:
		for preprosition in prepositions:
			if verb in sentence and preprosition in sentence:
				currentProp = str(find_between(sentence.lower(), verb+" ", " "+preprosition))
				if currentProp is not None and currentProp != "" and currentProp != " "   and ( bestProp is None or len(bestProp) < len(currentProp)):
					bestProp = currentProp
	if bestProp is None:
		return None
	return getSimilarWords(removeArticles(bestProp))

# Get redirected URI if it redirects
def getRedirectedURI(URI):
	redirectURIList = getRedirectPage(URI)
	if redirectURIList is None or redirectURIList is [] or len(redirectURIList) < 1:
		return URI
	return redirectURIList[0]

# Check if the exact name is found in the Names corpus
def inNamesCorpus(string):
	for line in open(v.FILE_NAMES, "r"):
		if re.search("^"+string+"$", line , re.IGNORECASE):
			return True
	return False

# DOES NOT WORK CORRECTLY
def matchSynonymProperty(synonyms, properties):
	#return sorted list of most likely properties
	bestMatches = []
	for property in properties:
		currentMax = 0
		for synonym in synonyms:
			similarity = difflib.SequenceMatcher(a=property, b=synonym).ratio()
			if similarity > currentMax:
				currentMax = similarity
		bestMatches.append([currentMax, property])
	return [t[1] for t in sorted(bestMatches, reverse=True)]

def isURI(string):
	if string is not None and "http://nl.dbpedia.org/resource/" in string:
		return True
	return False

# Returns true if wantedTypeName is in the list types, else false
def findType(types, wantedTypeName):
	allTypes = []
	for currentType in types:
		if wantedTypeName.lower() in currentType.lower():
			return True
		#if "http://dbpedia.org/ontology/" in currentType:
		#	allTypes.append(currentType.split("http://dbpedia.org/ontology/",1)[1])
	return False

# Returns whether the URI contains one of the wanted types.
def typesInURI(URI, wantedTypeNames):
	types = queryGetTypes(URI)
	v.printDebug(types)
	for name in wantedTypeNames:
		if findType(types, name):
			return True
	return False

# get URI of answer
def getExpectedAnswerURI(answer):
	URI = answer
	if not isURI(answer):
		URI  = getDomainURI(answer)
	return URI

def isExpectedAnswerPerson(answer,dataType):
	if dataType is not None and (dataType == v.DATATYPE_DATE or dataType == v.DATATYPE_INTEGER):
		return False
	v.printDebug("DATATYPE = "+ str(dataType))
	URI = answer
	title = answer

	for passWord in v.PASS_PERSON:
		if passWord in answer:
			return True
	if not isURI(answer):
		URI = getExpectedAnswerURI(answer)
	if isURI(answer):
		URI = getRedirectedURI(URI)
		if typesInURI(URI, ["Person", "Agent"]):
			return True

		title = ""
		tempTitle = URITitle(URI)
		for item in tempTitle:
			title += str(item)

	if len(title) < 1:
		return False

	names = title.split(" ")
	for name in names:
		if name.isupper() and inNamesCorpus(name):
			v.printDebug("FOUND NAME IN CORPUS " + str(name))
			return True
	return False

#TODO probably not 100% correct
def isExpectedAnswerLocation(answer,dataType):
	if dataType is not None and (dataType == v.DATATYPE_DATE or dataType == v.DATATYPE_INTEGER):
		return False
	URI = answer
	v.printDebug("url: "+str(URI))
	answerSplit = answer.split(",")
	count = 0
	v.printDebug(answerSplit)
	while count < len(answerSplit) and not isURI(URI):
		currentAnswer = makeAZ(answerSplit[count])
		v.printDebug(getExpectedAnswerURI(str(currentAnswer)))
		URI = getExpectedAnswerURI(str(currentAnswer))
		count += 1
	if URI is None:
		return False
	URI = getRedirectedURI(URI)
	if typesInURI(URI, ["Location", "Place", "Country", "City"]):
		return True
	return False

def isExpectedAnswerDate(answer,dataType):
	# check xsd:date
	#can't be date if it is a uri
	v.printDebug("DATE"+str(answer))
	#if not isURI(answer):
	if dataType is not None and dataType == v.DATATYPE_DATE:
		return True
	return False

def isExpectedAnswerNumber(answer,dataType):
	# check xsd:integer
	v.printDebug(dataType)
	if dataType is not None and dataType == v.DATATYPE_INTEGER:
		return True
	if (dataType == None or dataType == v.DATATYPE_STRING) and not isURI(answer):
		AZAnswer = makeAZ(answer)
		letterCount = 0
		for letter in AZAnswer:
			if letter.isdigit():
				letterCount += 1
		if (letterCount/len(AZAnswer)) >= 0.5:
			return True
	return False

def isExpectedAnswerObject(answer, dataType):
	# Unsure how to check this
	return True

# Give answer and expectedAnswer and it uses it to go to sub functions
def isExpectedAnswerSwitch(answer, dataType, expectedAnswer):
	if expectedAnswer == v.ANSWER_PERSON:
		return isExpectedAnswerPerson(answer, dataType)
	elif expectedAnswer == v.ANSWER_LOCATION:
		return isExpectedAnswerLocation(answer, dataType)
	elif expectedAnswer == v.ANSWER_DATE:
		return isExpectedAnswerDate(answer, dataType)
	elif expectedAnswer == v.ANSWER_NUMBER:
		return isExpectedAnswerNumber(answer, dataType)
	elif expectedAnswer == v.ANSWER_OBJECT:
		return isExpectedAnswerObject(answer, dataType)
	# Return True if expectedAnswer == ANSWER_UNKNOWN or something else
	return True

#Check if it is the expected Answer type
def isExpectedAnswer(answer,dataTypes, expectedAnswer):
	counter = 0
	if expectedAnswer == v.ANSWER_UNKNOWN:
		return True

	for answerItem in answer:
		currentDataType = None
		if not dataTypes is None:
			currentDataType = dataTypes[counter]
		# Test: If only one answer returns the right type, return True
		#if not isExpectedAnswerSwitch(answerItem, currentDataType, expectedAnswer):
		#	return False
		if isExpectedAnswerSwitch(answerItem, currentDataType, expectedAnswer):
			return True
		counter += 1
	# Change to True if all have to be correct 
	return False


#TODO: -for each type of question, add function to parse it
#- send parsed information to correct SPARQL query template

def getResource(concept):
	URI = None
	URI = getDomainURI(concept)
	if URI == None:
		# Remove articles from domain
		# TODO only remove first article
		URI = getDomainURI(removeArticles(concept))
		if URI == None:
			# No URI found
			v.printDebug("NO URI FOUND IN XofY")
			v.printDebug(concept)
			return None

	return URI

def parseConceptProperty(concept,property, expectedAnswer):
	answers = None
	firstAnswer = None
	titles = None
	dataTypes = None
	URI = None
	v.printDebug("found concept: "+str(concept)+"property: "+str(property))
	#find URI of concept
	if type(concept) is not list:
		concept = [concept]

	for c in concept:
		URI = getResource(c)
		if URI != None:
			break
	

	#find properties of the concept
	URIprops = findProperties(URI)
	v.printDebug(URIprops)

	#match properties using synonyms
	synonyms = getSimilarWords(property)
	v.printDebug(synonyms)

	#TODO bestMatches lijkt het niet goed te doen
	bestMatches = matchSynonymProperty(synonyms, URIprops)

	#go through properties until expected answer is found
	#TODO: only terminate if answer matches expected answer!
	#TODO not only get answers, also get the XML information of the answer so it can classify correctly
	for property in bestMatches:
		v.printDebug (property)
		answers,titles,dataTypes = queryXofY(property, URI, True)
		if answers == None or answers == []:
			continue
		v.printDebug(answers)
		v.printDebug(expectedAnswer)
		if not isExpectedAnswer(answers,dataTypes, expectedAnswer):
			answers = None
			continue
		else:
			break
	# Return the first answer found, At least it gives an answer
	if answers == None:
		return titles
	return titles


# Parse question of type "Wie/wat is X van Y"
def parseXofY(xml, expectedAnswer):
	answers = None
	firstAnswer = None
	titles = None
	concept = None
	dataTypes = None
	property = None

    #find concept
	concepts = xml.xpath('//node[@rel="obj1" and ../@rel="mod" and (../../@rel="su" or ../../@rel="predc" )]', smart_strings=False)
    #concepts = xml.xpath('//node[@rel="obj1" and ../@rel="mod"]')
    #find property
	#properties = xml.xpath('//node[@rel="hd" and ../@rel="su"]')
	properties = xml.xpath('//node[@pos="noun" and (../@rel="su" or ../@rel="predc")]', smart_strings=False)
	for name in concepts:
		concept = getTreeWordList(name,v.TYPE_WORD)
	if concept==None or concept=="":
		return None
	for name in properties:
		property = getTreeWordList(name,v.TYPE_LEMMA)
	if property==None or property=="":
		v.printDebug("NO PROPERTY FOUND")
		return None

	return parseConceptProperty(concept, property, expectedAnswer)


def parseWhereWhen(xml, expectedAnswer):
	#maybe idea to split the parse into more functions, lot of duplicate code this way.
	#Waar is Sven Kramer geboren werkt /wanneer geboren niet. Pakt nog steeds geboorteplaats als property
	answers = None
	firstAnswer = None
	titles = None
	dataTypes = None
	concept = []
	property = None
	concepts =[]

	t = xml.xpath('//node[@rel="whd" and (@frame="er_wh_loc_adverb" or @frame="wh_tmp_adverb")]')
	t=t[0]
	if t.xpath('//node[@rel="hd" and ../@cat="ppart"]', smart_strings=False):
		prop =  t.xpath('//node[@rel="hd" and ../@cat="ppart"]', smart_strings=False);
	else:
		prop =  t.xpath('//node[@rel="hd" and ../@rel="body"]', smart_strings=False);
	concepts.append(t.xpath('//node[@rel="su" and ../@rel="body"]', smart_strings=False)[0]);
	c = t.xpath('//node[@rel="obj1" and ../../@rel="su" and ../../../@rel="body"]', smart_strings=False)
	if c:
		concepts.append(c[0]);

	for name in concepts:
		concept.append(getTreeWordList(name,v.TYPE_WORD))
	if concept==None or concept=="" or (not concept):
		return None

	for name in prop:
		property = getTreeWordList(name,v.TYPE_LEMMA)
	if property==None or property=="":
		v.printDebug("NO PROPERTY FOUND")
		return None

	return parseConceptProperty(concept,property, expectedAnswer)

def parseHow(xml, expectedAnswer):
	answers = None
	firstAnswer = None
	titles = None
	dataTypes = None
	concept = None
	t = xml.xpath('//node[@rel="whd" and @cat="ap"]')[0]
	prop =  t.xpath('//node[@rel="hd"]', smart_strings=False)
	concepts =  t.xpath('//node[@rel="su" and ../@rel="body"]', smart_strings=False)

	for name in concepts:
		concept = getTreeWordList(name,v.TYPE_WORD)
	if concept==None or concept=="":
		return None

	property = getTreeWordList(prop[0],v.TYPE_WORD)
	if property==None or property=="":
		v.printDebug("NO PROPERTY FOUND")
		return None
	return parseConceptProperty(concept,property, expectedAnswer)

def parseVerbs(xml, expectedAnswer):
	answers = None
	firstAnswer = None
	titles = None
	dataTypes = None
	concept = None
	#//node[@rel="hd" and @pt="ww"]
	#t = xml.xpath('//node[@rel="su" and ../@rel="body" and @index and not(@cat)]')[0]
	#t=t[0]
	#	index = t.get("index");
	#	query = '//node[@index ="'+index+'"]'
	#	part_prop = xml.xpath(query)[0].get("root")

	#print_tree( xml.xpath('//node[@rel="hd" and @stype="whquestion" and ../@rel="body"]', smart_strings=False)[0])
	prop = xml.xpath('//node[@rel="hd" and @pt="ww"]', smart_strings=False)#stype="whquestion"
	concepts =  xml.xpath('//node[@cat="np" and (../@rel="body" or ../../@rel="body")]', smart_strings=False);

	for name in concepts:
		concept = getTreeWordList(name,v.TYPE_WORD)
	if concept==None or concept=="":
		return None

	property = getTreeWordList(prop[0],v.TYPE_LEMMA)
	if property==None or property=="":
		v.printDebug("NO PROPERTY FOUND")
		return None
	return parseConceptProperty(concept,property, expectedAnswer)


# Parse question which wants a number
def parseNumberOf(xml, expectedAnswer):
	# First check URI for number solutions
	# Else create a listing query which somehow answers question

	return None
