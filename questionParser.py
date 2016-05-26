import sys, re, difflib
import variables as v
from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLQuery import queryXofY

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

#TODO: -for each type of question, add function to parse it
#- send parsed information to correct SPARQL query template

# Parse question of type "Wie/wat is X van Y"
def parseXofY(xml, expectedAnswer):
    #find concept
    names = xml.xpath('//node[@rel="obj1" and ../@rel="mod"]')
    for name in names:
        concept = getTreeWordList(name,v.TYPE_LEMMA)
    if concept==None or concept=="":
        return None
    #find property
    names = xml.xpath('//node[@rel="hd" and ../@rel="su"]')
    for name in names:
        property = getTreeWordList(name,v.TYPE_LEMMA)
    if property==None or property=="":
        return None

    #find URI of concept
    URI = getDomainURI(concept)

    #find properties of the concept
    props = findProperties(URI)

    #match properties using synonyms
    synonyms = getSimilarWords(property)
    bestMatches = matchSynonymProperty(synonyms, props)

    #go through properties until expected answer is found
    #TODO: only terminate if answer matches expected answer!
    answer = None
    for property in bestMatches:
        print (property)
        if answer != None and answer != []:
            break
        answer = queryXofY(property, URI)
    return answer

# Parse question which wants a number
def parseNumberOf(xml, expectedAnswer):
    # First check URI for number solutions
    # Else create a listing query which somehow answers question

    return None
