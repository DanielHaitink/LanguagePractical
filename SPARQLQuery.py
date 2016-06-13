import re
import variables as v
from SPARQLWrapper import SPARQLWrapper, JSON

# Query is query to be asked, getDataType must be True OR False
def sendQuery(query, getDataType): #returns list of answers for a SPARQL query
	dataTypes = []
	answer = []

	sparql = SPARQLWrapper("http://nl.dbpedia.org/sparql")
	sparql.setQuery(query)
	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()

	for result in results["results"]["bindings"]:
		for arg in result :
			answer.append(result[arg]["value"])

			# if it contains a Datatype, add it. Else add None
			if len(result[arg]) > 2:
				dataTypes.append(result[arg]["datatype"])
			else:
				dataTypes.append(None)
	# If datatypes and answer are not of the same length say so
	if getDataType and len(dataTypes) != len(answer):
		v.printDebug("!!WARNING!! LENGTH OF DATATYPES IS UNEQUAL TO LENGTH OF ANSWERS")

	# Return datatypes and answers if wanted, else just answer
	if getDataType:
		return answer, dataTypes
	return answer

# Default query for most parsers, not just XofY
def queryXofY(property, URI, getDataType, prefix='prop-nl:'):
	dataTypes = None
	titles = []
	answers = []

	query = """
	SELECT ?answer

	WHERE{
	<%s> %s%s ?answer
	}
	""" % (URI,prefix, property)

	q2 = """
	SELECT ?answer

	WHERE{
	?answer %s%s <%s>
	}
	""" % (prefix, property,URI)
	v.printDebug(query)

	if getDataType:
		answers, dataTypes = sendQuery(query, getDataType)
		if not answers:
			v.printDebug("andersom question")
			answers,dataTypes = sendQuery(q2, getDataType)
	else:
		answers = sendQuery(query, False)
		if not answers:
			v.printDebug("andersom question")
			answers = sendQuery(q2, False)
	for answer in answers:
		if "nl.dbpedia" in answer:
			title = URITitle(answer)
			if title != []:
				titles.append(title[0])
			else:
				titles.append(answer)
		else:
			titles.append(answer)
	if getDataType:
		return answers, titles, dataTypes
	return answers, titles

# Basic query to obtain a specific property from a single URI
def basicQuery(URI, property):
	query = """
	SELECT ?answer
	WHERE{
	<%s> %s ?answer
	}
	""" % (URI,property)
	return sendQuery(query, False)

# Get the title of the URI
def URITitle(URI):
	return basicQuery(URI, "rdfs:label")

# Get the redirected page of the URI
def getRedirectPage(URI):
	return basicQuery(URI, "dbpedia-owl:wikiPageRedirects")

# Query for the type checking
def queryGetTypes(URI):
	return basicQuery(URI, "rdf:type")
