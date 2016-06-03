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
            if len(result[arg]) > 2:
                dataTypes.append(result[arg]["datatype"])
            else:
                dataTypes.append(None)

    if getDataType and len(dataTypes) != len(answer):
        v.printDebug("!!WARNING!! LENGTH OF DATATYPES IS UNEQUAL TO LENGTH OF ANSWERS")
    if getDataType:
        return answer, dataTypes
    return answer

#TODO: create templates for SPARQL query for each question type


def queryXofY(property, URI, getDataType):
    dataTypes = None
    titles = []
    answers = []

    query = """
    SELECT ?answer

    WHERE{
    <%s> prop-nl:%s ?answer
    }
    """ % (URI,property)

    q2 = """
    SELECT ?answer

    WHERE{
    ?answer prop-nl:%s <%s>
    }
    """ % (property,URI)
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

def basicQuery(URI, property):
    query = """
    SELECT ?answer
    WHERE{
    <%s> %s ?answer
    }
    """ % (URI,property)
    return sendQuery(query, False)

def URITitle(URI):
    return basicQuery(URI, "rdfs:label")

def getRedirectPage(URI):
    return basicQuery(URI, "dbpedia-owl:wikiPageRedirects")

# QUery for the type checking
def queryGetTypes(URI):
    return basicQuery(URI, "rdf:type")
