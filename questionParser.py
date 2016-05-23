import sys, re
import variables as v

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
def getDomainURI(domain):
	PCList = search(domain+"#", FILE_PAIRCOUNT)
	if len(PCList) is 0:
		return None
	bestItem = getHighestPairCount(PCList)
	return findBetween(bestItem, "\t", "\t")

#Removes everything from string except numbers and letters
def makeAZ(string):
	return re.sub(r'[\W_]+', '', string)

#TODO: -for each type of question, add function to parse it
#- send parsed information to correct SPARQL query template
