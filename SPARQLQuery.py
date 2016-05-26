import re
from SPARQLWrapper import SPARQLWrapper, JSON

def sendQuery(query): #returns list of answers for a SPARQL query
    sparql = SPARQLWrapper("http://nl.dbpedia.org/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    answer = []

    for result in results["results"]["bindings"]:
        for arg in result :
            answer.append(result[arg]["value"])

    return answer

#TODO: create templates for SPARQL query for each question type

def queryXofY(property, URI):
    query = """
    SELECT str(COALESCE(?answer2,?answer)) as ?answer

    WHERE{
    <%s> prop-nl:%s ?answer
    OPTIONAL{?answer rdfs:label ?answer2}
    }
    """ % (URI,property)

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
