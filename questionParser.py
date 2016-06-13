import sys, re, difflib
import variables as v
import io
from datetime import date
#from dateutil.relativedelta import relativedelta
from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLQuery import queryXofY, queryGetTypes, URITitle, getRedirectPage, basicQuery

# Find all properties that the given URI has
def findProperties(URI, both=True):
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
	if both:
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
#exclude most contain a list of arrays, where an array is [attrib, value], there words will be filtered out of the result
def getTreeWordList(xml, wordtype, exclude=[]):
	#appends the value of the word-attribute for all nodes that are dominated by the node 'xml'
	#that is the argument of the function, and returns this a single string
	leaves = xml.xpath('descendant-or-self::node[@word]')
	words = []
	for l in leaves :
		add = True
		for p in exclude:
			if (l.attrib[p[0]] == p[1]):
				add = False
				break
		if add:
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
		if re.search("(^|#)"+query+"#", line , re.IGNORECASE):
			outList.append(line)
	return outList

def getKeyOS(item):
    return item[1]

def checkWhichOS(concept):
	v.printDebug("checking which os we need")
	result =[]
	r = []
	w = v.SPECIFIC_OS_CHECK
	words = concept.lower().split(' ')
	for word in w:

		if word in words:
			if word in ['laatste','vorige']:
				prop =  "dbpedia-owl:previousEvent"
			elif word in ['volgende', 'aankomende', 'eerstvolgende']:
				prop = "dbpedia-owl:nextEvent"
			elif word in ['eerste']:
				prop = "prop-nl:eerste"
			reg = re.search("Olympische (.)*spelen", concept, re.IGNORECASE)


			#safety check
			if reg is None:
				return False

			#ugly but database lacks consistency so a bit nore of hardcoding
			if (prop == "prop-nl:eerste"):
				if(reg.group().lower == "olympische zomerspelen"):
					return("http://nl.dbpedia.org/resource/Olympische_Zomerspelen_1896")
				elif(reg.group().lower == "olympische winterspelen"):
					return('http://nl.dbpedia.org/resource/Olympische_Winterspelen_1924')
			v.printDebug("found pattern"+str(reg.group()))
			#ugly fix with tab, to prevent Zomerspelen 2012 to be selected...
			URI = getDomainURI(reg.group()+"\t")
			v.printDebug("uri found: "+str(URI))
			URI =basicQuery(URI, prop)
			v.printDebug("osanswer: "+str(URI))
			for u in URI:
				if isURI(u):
					result.append(u)

			if len(result)>1 and (word == 'volgende' or word == 'vorige'):
				desc = False
				for item in result:
					jaar = basicQuery(item,"prop-nl:jaar")
					if type(jaar) is list and jaar:
						jaar = jaar[0]
					r.append([item, int(jaar)])
				if(word == 'vorige'):
					desc = True

				r = sorted(r, key=getKeyOS,  reverse=desc)
				v.printDebug("found os: "+str(r[0][0]))
				return r[0][0]

			elif result:
				v.printDebug("found os: "+str(result[0]))
				return result[0]
	return False

#gives the URI of a given concept
def getDomainURI(concept):
	max = 0
	URI = None
	words = None

	#check if eerste/volgende/vorige spelen
	checkWhich = checkWhichOS(concept)
	if checkWhich:
		return checkWhich

	#io.open also works on windows with unix utf-8 files
	for line in io.open(v.FILE_PAIRCOUNT, 'r', encoding='utf-8'):
	#for line in open(v.FILE_PAIRCOUNT, 'r'):
		if re.search("^"+concept, line, re.IGNORECASE): #search concept in pairCounts
			#v.printDebug(line)
			line = line.rstrip()
			line = line.split("\t") #split lines by tabs to separate elements
			if len(line) > 1 and int(line[2])>max: #if occurcences is higher than the maximum found until now:
				max = int(line[2]) #new maximum amount of occurences
				URI = line[1] #store URI
	return URI

def specificOS(sentence):
	s = re.search("\w+ Olympische \w*spelen", sentence, re.IGNORECASE)
	if s is not None:
		w = v.SPECIFIC_OS_CHECK
		words = s.group().lower().split(' ')
		for word in w:
			if word in words:
				return checkWhichOS(s.group())
	return False


#alternative way of finding concept by comparing entire sentence to entries in pairCounts
def patheticConceptFinder(sentence):
	t =specificOS(sentence)
	if t:
		return t
	v.printDebug("No concept found, desperately trying to find one using difflib")
	URI = None
	similarityMax = 0
	for line in io.open(v.FILE_PAIRCOUNT, 'r', encoding='utf-8'):
		line = line.rstrip()
		line = line.split("\t")
		if len(line)>2:
			if line[0].lower() in sentence.lower():
				similarity = difflib.SequenceMatcher(a=line[1], b=sentence).ratio()
				if similarity > similarityMax:
					similarityMax = similarity
					URI = line[1]
	v.printDebug("Found concept:" + URI)
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

def removeUnderscore(string):
	return string.replace("_", "")

def replaceUnderscore(string, replace = " "):
	return string.replace("_", " ")

#search fot similar words
def getSimilarWords(string):
	returnList = []
	searchList = search(string, v.FILE_SYNONYMS)
	if not searchList:
		searchList = search(removeUnderscore(string), v.FILE_SYNONYMS)
		if not searchList:
			searchList = search(replaceUnderscore(string), v.FILE_SYNONYMS)

	for item in searchList:
		#split line into words
		for word in item.split("#"):
			#check if word is not already in list and it is not an enter
			if word not in returnList and word != "\n":
				returnList.append(word)
		#returnList += item.split("#")
	if not returnList:
		returnList.append(string)
	return returnList

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

#Match a list of synonyms and a list of properties from a URI to find the best match
def matchSynonymProperty(synonyms, properties, threshold = v.SIMILARITY_THRESHOLD):
	#return sorted list of most likely properties
	bestMatches = []
	for property in properties:
		currentMax = 0
		for synonym in synonyms:
			similarity = difflib.SequenceMatcher(a=property, b=synonym).ratio()
			if similarity > currentMax:
				currentMax = similarity
		if currentMax > threshold: #only if similarity is higher than 0.4
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

def isInDataType(inputDataType, checkDataType):
	for item in checkDataType:
		if inputDataType == item:
			return True
	return False

# get URI of answer
def getExpectedAnswerURI(answer):
	URI = answer
	if not isURI(answer):
		URI  = getDomainURI(answer)
	return URI

#check if the answer is a person
def isExpectedAnswerPerson(answer,dataType):
	if dataType is not None and (isInDataType(dataType, v.DATATYPE_DATE) or isInDataType(dataType, v.DATATYPE_INTEGER)):
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
		if len(name) > 0 and name[0].isupper() and inNamesCorpus(name):
			v.printDebug("FOUND NAME IN CORPUS " + str(name))
			return True
	return False

#check if the answer is a location
def isExpectedAnswerLocation(answer,dataType):
	if dataType is not None and (isInDataType(dataType, v.DATATYPE_DATE) or isInDataType(dataType, v.DATATYPE_INTEGER)):
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
	#if page has property inwoners, assume it is a location
	#maybe more are to be added
	prop = findProperties(URI, both=False)
	for p in prop:
		if p == "inwoners":
			return True;
	return False

#check if the answer is a date
def isExpectedAnswerDate(answer,dataType):
	# check xsd:date
	#can't be date if it is a uri
	v.printDebug("DATE"+str(answer))
	#if not isURI(answer):
	if dataType is not None and isInDataType(dataType, v.DATATYPE_DATE):
		return True
	return False

#check if the answer is a number
def isExpectedAnswerNumber(answer,dataType):
	# check xsd:integer
	v.printDebug(dataType)
	if dataType is not None and isInDataType(dataType, v.DATATYPE_INTEGER):
		return True
	if ((dataType == None or not isInDataType(dataType, v.DATATYPE_DATE)) and not isURI(answer)):
		AZAnswer = makeAZ(answer)
		letterCount = 0
		for letter in AZAnswer:
			if letter.isdigit():
				letterCount += 1
		if len(AZAnswer) > 0  and (letterCount/len(AZAnswer)) >= 0.5:
			return True
	return False

#check if the answer is an object
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

#get a URI from a concept
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

#check if a person is dead, to find correct age
def isDead(URI):
	deathDate = basicQuery(URI, "dbpedia-owl:deathDate")
	if deathDate != None and deathDate != []:
		 return True
	return False

def parseTimeDifference(URI, beginDate,beginPrefix="prop-nl:", endDate = 'now', endPrefix="prop-nl:", showIn='years'):
	#only now works for years
	#other stuff can be added if one feels the need to do so
	v.printDebug("use parseTimeDifference")
	answers,titles = queryXofY(beginDate, URI, False, prefix=beginPrefix)
	if not answers:
		answers = titles
	if answers:
		d = answers[0].split('-')
		print(date)
		begin = date(int(d[0]), int(d[1]), int(d[2]))
	else:
		return None

	if(endDate == "now"):
		end = date.today()
		v.printDebug("got enddate as today")
	else:
		answers,titles = queryXofY(endDate, URI, False, prefix=endPrefix)
		if not answers:
			answers = titles
		if answers:
			d = answers[0].split('-')
			end = date(int(d[0]), int(d[1]), int(d[2]))
		else:
			return None
	if(showIn=="years"):
		years =  end.year - begin.year
		if(end.month < begin.month):
			years -= 1
		elif(end.month == begin.month and end.day < begin.day):
			years -= 1
	return [(str(years)+ " jaar")]

#given a concept and a list of possible properties, try to retrieve an answer from dbpedia
def parseConceptProperty(concept,property, expectedAnswer, sentence, threshold = v.SIMILARITY_THRESHOLD):
	answers = None
	firstAnswer = None
	titles = None
	dataTypes = None
	URI = None
	v.printDebug("found concept: "+str(concept)+" property: "+str(property))
	v.printDebug("expected answer: "+ str(expectedAnswer))

	#if property is Olympische spelen and expected answer is location, then we know we need the location of the Olympic games then
	if(expectedAnswer== v.ANSWER_LOCATION and (property.strip().lower() == 'olympische zomerspelen' or property.strip().lower() == 'olympische winterspelen' or property.strip().lower() == 'olympische spelen')):
		property = "locatie"


	#find URI of concept
	if type(concept) is not list:
		concept = [concept]

	for c in concept:
		if "nl.dbpedia" not in c:
			URI = getResource(c)
			if URI != None:
				break
			else:
				URI = patheticConceptFinder(sentence)
		else:
			URI = c

	if(property == "oud" or property == "leeftijd"):
		if isDead(URI):
			return ["Overleden"]
		return parseTimeDifference(URI,"birthDate", beginPrefix="dbpedia-owl:")

	#find properties of the concept
	URIprops = findProperties(URI)
	v.printDebug(URIprops)

	#match properties using synonyms
	synonyms = getSimilarWords(property)
	v.printDebug(synonyms)

	bestMatches = matchSynonymProperty(synonyms, URIprops, threshold)

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
	v.printDebug(titles)
	if answers == None:
		return titles
	return titles

# Parse question of type "Wie/wat is X van Y"
def parseXofY(xml, expectedAnswer, sentence):
	answers = None
	firstAnswer = None
	titles = None
	concept = None
	dataTypes = None
	property = None

    #find concept
	concepts = xml.xpath('//node[@rel="obj1" and ../@rel="mod" and (../../@rel="su" or ../../@rel="predc" )]', smart_strings=False)
	properties = xml.xpath('//node[@rel="hd" and ../@rel="whd" and not(@word="Aan")]')

	for name in concepts:
		concept = getTreeWordList(name,v.TYPE_WORD)
	if concept==None or concept=="":
		#parser for welke question
		v.printDebug("Trying to parse for welke question!")
		concepts = xml.xpath('//node[@rel="su" and ../@rel="body"]')
		for name in concepts:
			concept = getTreeWordList(name,v.TYPE_WORD)
	if concept==None or concept=="":
		concept = patheticConceptFinder(sentence)
	if concept==None or concept=="":
		v.printDebug("No concept found!")
		return None
	for name in properties:
		property = getTreeWordList(name,v.TYPE_LEMMA)
	if property==None or property=="" or property == concept:
		properties = xml.xpath('//node[@pos="noun" and (../@rel="su" or ../@rel="predc")]', smart_strings=False)
		for name in properties:
			property = getTreeWordList(name,v.TYPE_LEMMA)
	if property==None or property=="":
		properties = xml.xpath('//node[@rel="hd" and @pos="noun"]', smart_strings=False)
		for name in properties:
			property = getTreeWordList(name,v.TYPE_LEMMA)
	if property==None or property=="":
		v.printDebug("NO PROPERTY FOUND")
		return None
	return parseConceptProperty(concept, property, expectedAnswer, sentence)


def parseWhereWhen(xml, expectedAnswer, sentence):
	answers = None
	firstAnswer = None
	titles = None
	dataTypes = None
	concept = []
	property = None
	concepts =[]

	t = xml.xpath('//node[@rel="whd" and (@frame="er_wh_loc_adverb" or @frame="wh_tmp_adverb")]')
	t=t[0]
	if t.xpath('//node[@rel="hd" and ../@cat="ppart" ]', smart_strings=False):
		prop =  t.xpath('//node[@rel="hd" and ../@cat="ppart" and not(@lemma="zijn")]', smart_strings=False);
	else:
		prop =  t.xpath('//node[@rel="hd" and ../@rel="body" and not(@lemma="zijn")]', smart_strings=False);
	if t.xpath('//node[@rel="su" and ../@rel="body"]', smart_strings=False):
		concepts.append(t.xpath('//node[@rel="su" and ../@rel="body"]', smart_strings=False)[0]);
	c = t.xpath('//node[@rel="obj1" and ../../@rel="su" and ../../../@rel="body"]', smart_strings=False)
	if c:
		concepts.append(c[0]);

	#filter questions with only zijn als ww and not a past particle
	if not prop:
		prop =  t.xpath('//node[@rel="hd" and ../@rel="su" and ../../@rel="body" and not(@lemma="zijn")]', smart_strings=False);

		if t.xpath('//node[@rel="predc" and ../@rel="body"]', smart_strings=False):
			concepts = []
			concepts.append(t.xpath('//node[@rel="predc" and ../@rel="body"]', smart_strings=False)[0]);

	for name in concepts:
		concept.append(getTreeWordList(name,v.TYPE_WORD))
	if concept==None or concept=="":
		concept = patheticConceptFinder(sentence)
	if concept==None or concept=="":
		v.printDebug("No concept found!")
		return None

	for name in prop:
		property = getTreeWordList(name,v.TYPE_LEMMA)
	if property==None or property=="":
		v.printDebug("NO PROPERTY FOUND")
		return None

	return parseConceptProperty(concept,property, expectedAnswer, sentence)

def parseHow(xml, expectedAnswer, sentence):
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
		concept = patheticConceptFinder(sentence)
	if concept==None or concept=="":
		v.printDebug("No concept found!")
		return None

	property = getTreeWordList(prop[0],v.TYPE_WORD)
	if property==None or property=="":
		v.printDebug("NO PROPERTY FOUND")
		return None
	return parseConceptProperty(concept,property, expectedAnswer, sentence)

def parseVerbs(xml, expectedAnswer, sentence):
	answers = None
	firstAnswer = None
	titles = None
	dataTypes = None
	property = None
	concept = None

	prop = xml.xpath('//node[@rel="hd" and @pt="ww" and not (@lemma="hebben" or @lemma="worden" or @lemma="zijn")]', smart_strings=False)#stype="whquestion"
	concepts =  xml.xpath('//node[@cat="np" and (../@rel="body" or ../../@rel="body")]', smart_strings=False);

	for name in concepts:
		concept = getTreeWordList(name,v.TYPE_WORD)
	if concept==None or concept=="":
		concept = patheticConceptFinder(sentence)
	if concept==None or concept=="":
		v.printDebug("No concept found!")
		return None

	if prop:
		property = getTreeWordList(prop[0],v.TYPE_LEMMA)
	if property==None or property=="":
		v.printDebug("NO PROPERTY FOUND")
		return None
	return parseConceptProperty(concept,property, expectedAnswer, sentence)


# Parse question which wants a number
def parseNumberOf(xml, expectedAnswer, sentence):
	answers = None
	firstAnswer = None
	titles = None
	dataTypes = None
	property = ""
	concept = ""
	c = ""

	# First check URI for number solutions
	# Else create a listing query which somehow answers question
	properties = xml.xpath('//node[(@rel="mod" and ../@rel="whd") or (@rel="hd" and ../@rel="whd")]')
	concepts = xml.xpath('//node[(@rel="mod" and ../@rel="body") or @rel="su"]')
	for name in concepts:
		concept = concept + getTreeWordList(name,v.TYPE_WORD) + " "
		concept = concept.strip()
	if concept==None or concept=="" or concept == " ":
		concepts = xml.xpath('//node[@rel="obj1" and ../@rel="body"]')
		for name in concepts:
			concept = concept + " " +getTreeWordList(name,v.TYPE_WORD) + " "
		concept = concept.strip()
	if concept==None or concept=="" or concept == " ":
		concepts = xml.xpath('//node[@rel="obj1" and (../@rel="body" or ../../@rel="body")]')
		for name in concepts:
			concept = concept + " " +getTreeWordList(name,v.TYPE_WORD) + " "
		concept = concept.strip()

	concept = concept.strip()

	concepts = xml.xpath('//node[@rel="body" and ../@cat="whq"]')

	for name in concepts:
		c =getTreeWordList(name,v.TYPE_WORD, exclude = [['pos','verb']])

	if concept==None or concept=="" or concept == " ":
		concept = c
	elif c and not c=="":
		concept = [c, concept]

	v.printDebug("concept" + str(concept))
	if concept==None or concept=="":
		concept = patheticConceptFinder(sentence)
	if concept==None or concept=="":
		v.printDebug("No concept found!")
		return None

	for name in properties:
		property = property + getTreeWordList(name,v.TYPE_WORD) + " "
	if property==None or property=="":
		v.printDebug("NO PROPERTY FOUND")
		return None

	property = property.strip()
	v.printDebug(property)
	v.printDebug(concept)

	answer = parseConceptProperty(concept,property, expectedAnswer, sentence)

	if answer != None and len(answer)>1:
		return [len(answer)]
	else:
		return answer
