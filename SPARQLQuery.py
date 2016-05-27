import re
import variables as v
from SPARQLWrapper import SPARQLWrapper, JSON

def sendQuery(query): #returns list of answers for a SPARQL query
    sparql = SPARQLWrapper("http://nl.dbpedia.org/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    answer = []
    v.printDebug(results)
    for result in results["results"]["bindings"]:
        for arg in result :
            answer.append(result[arg]["value"])

    return answer

#TODO: create templates for SPARQL query for each question type


def queryXofY(property, URI):
    query = """
    SELECT ?answer

    WHERE{
    <%s> prop-nl:%s ?answer
    }
    """ % (URI,property)

    titles = []
    answers = sendQuery(query)
    for answer in answers:
        if "nl.dbpedia" in answer:
            title = URITitle(answer)
            if title != []:
                titles.append(title[0])
            else:
                titles.append(answer)
        else:
            titles.append(answer)
    return answers, titles

def URITitle(URI):
    query = """
    SELECT ?title
    WHERE{
    <%s> rdfs:label ?title
    }
    """ % (URI)

    return sendQuery(query)

# QUery for the type checking
def queryGetTypes(URI):
    query = """
    SELECT ?types

    WHERE{
    <%s> rdf:type ?answer
    }
    """ % (URI)
    return sendQuery(query)
