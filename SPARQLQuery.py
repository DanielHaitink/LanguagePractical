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
