import sys, re, difflib
import variables as v
from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLQuery import queryXofY, queryGetTypes

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
    if "http://" in string:
        return True
    return False

# Returns true if wantedTypeName is in the list types, else false
def findType(types, wantedTypeName):
    allTypes = []
    for currentType in types:
        if wantedTypeName in currentType:
            return True
        #if "http://dbpedia.org/ontology/" in currentType:
        #    allTypes.append(currentType.split("http://dbpedia.org/ontology/",1)[1])
    return False

# Returns whether the URI contains one of the wanted types.
def basicExpectedAnswer(answer, wantedTypeNames):
    URI = answer
    if not isURI(answer):
        URI  = getDomainURI(answer)
    if URI == None:
        v.printDebug("URI NOT FOUND IN isExpectedAnswerPerson")
        return False
    types = queryGetTypes(URI)
    for name in wantedTypeNames:
        if findType(types, name):
            return True
    return False

def isExpectedAnswerPerson(answer):
    if basicExpectedAnswer(answer, ["Person"]):
        return True
    return False

def isExpectedAnswerLocation(answer):
    if basicExpectedAnswer(answer, ["Location", "Place", "Country", "City"]):
        return True
    return False

def isExpectedAnswerDate(answer):
    # check xsd:date
    return True

def isExpectedAnswerNumber(answer):
    # check xsd:integer
    return True

def isExpectedAnswerObject(answer):
    # Unsure how to check this
    return True

# Give answer and expectedAnswer and it uses it to go to sub functions
def isExpectedAnswerSwitch(answer, expectedAnswer):
    if expectedAnswer == v.ANSWER_PERSON:
        return isExpectedAnswerPerson(answer)
    elif expectedAnswer == v.ANSWER_LOCATION:
        return isExpectedAnswerLocation(answer)
    elif expectedAnswer == v.ANSWER_DATE:
        return isExpectedAnswerDate(answer)
    elif expectedAnswer == v.ANSWER_NUMBER:
        return isExpectedAnswerNumber(answer)
    elif expectedAnswer == v.ANSWER_OBJECT:
        return isExpectedAnswerObject(answer)
    # Return True if expectedAnswer == ANSWER_UNKNOWN or something else
    return True

#Check if it is the expected Answer type
def isExpectedAnswer(answer, expectedAnswer):
    if expectedAnswer == v.ANSWER_UNKNOWN:
        return True
    for answerItem in answer:
        if not isExpectedAnswerSwitch(answerItem, expectedAnswer):
            return False
    return True


#TODO: -for each type of question, add function to parse it
#- send parsed information to correct SPARQL query template

# Parse question of type "Wie/wat is X van Y"
def parseXofY(xml, expectedAnswer):
    answer = None

    #find concept
    names = xml.xpath('//node[@rel="obj1" and ../@rel="mod"]')
    for name in names:
        concept = getTreeWordList(name,v.TYPE_WORD)
    if concept==None or concept=="":
        return None
    #find property
    names = xml.xpath('//node[@rel="hd" and ../@rel="su"]')
    for name in names:
        property = getTreeWordList(name,v.TYPE_LEMMA)
    if property==None or property=="":
        v.printDebug("NO PROPERTY FOUND")
        return None

    #find URI of concept
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
        print (property)
        answer = queryXofY(property, URI)
        if answer == None or answer == []:
            continue
        v.printDebug(answer)
        v.printDebug(expectedAnswer)
        if not isExpectedAnswer(answer, expectedAnswer):
            answer = None
            continue
        else:
            break
    return answer

# Parse question which wants a number
def parseNumberOf(xml, expectedAnswer):
    # First check URI for number solutions
    # Else create a listing query which somehow answers question

    return None
