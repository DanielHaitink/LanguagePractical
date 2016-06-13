import sys

# Show debug messages
__DEBUG__ = True

# threshold for the matchSynonymProperty function
SIMILARITY_THRESHOLD = 0.4

#Files
FILE_PAIRCOUNT = "Resources/pairCounts"
FILE_SYNONYMS = "Resources/synonyms"
FILE_NAMES = "Resources/names.txt"

#Types of words alpino
TYPE_SENSE = "sense"
TYPE_WORD = "word"
TYPE_ROOT = "root"
TYPE_LEMMA = "lemma"

#Expected answer
ANSWER_LOCATION = "location"
ANSWER_PERSON = "person"
ANSWER_DATE = "date"
ANSWER_NUMBER = "number"
ANSWER_OBJECT = "object"
ANSWER_UNKNOWN = None

#WHD words for expected answer
WHD_LOCATION = ["waar"]
WHD_PERSON = ["wie", "door wie"]
WHD_DATE = ["wanneer"]
WHD_NUMBER = ["hoeveel", "hoe"]
WHD_OBJECT = ["welke"]

# Passes for expected answers, if a pass is found it is assumed to be true
PASS_PERSON = ["sir", "madam", "Dame", "lord", "Lady", "Queen"]


# Words to check different Olympic Games
SPECIFIC_OS_CHECK = ['eerste','vorige','laatste','volgende','aankomende', 'eerstvolgende']



# Datatypes used for expected answers
DATATYPE_INTEGER = ["http://www.w3.org/2001/XMLSchema#integer",
"http://www.w3.org/2001/XMLSchema#double",
"http://www.w3.org/2001/XMLSchema#float",
"http://www.w3.org/2001/XMLSchema#negativeInteger",
"http://www.w3.org/2001/XMLSchema#nonNegativeInteger",
"http://www.w3.org/2001/XMLSchema#nonPositiveInteger",
"http://www.w3.org/2001/XMLSchema#positiveInteger"]
DATATYPE_DATE = ["http://www.w3.org/2001/XMLSchema#date",
"http://www.w3.org/2001/XMLSchema#gMonthDay",
"http://www.w3.org/2001/XMLSchema#gMonth",
"http://www.w3.org/2001/XMLSchema#gDay",
"http://www.w3.org/2001/XMLSchema#gYear",
"http://www.w3.org/2001/XMLSchema#gYearMonth",
"http://www.w3.org/2001/XMLSchema#dateTime"]
DATATYPE_STRING = ["http://www.w3.org/2001/XMLSchema#string"]

# Prints to stderr iff __DEBUG__ is True
def printDebug(debug):
	if __DEBUG__:
		print(debug, file=sys.stderr)

# Prints an exception to stderr iff __DEBUG__ is True
def printError(debug, exception):
	if __DEBUG__:
		print(debug+ " " + exception, file=sys.stderr)



#Example questions for easy testing
QUESTIONS = [
    "Hoe lang is Usain Bolt?",
    "Waar is Usain Bolt geboren?",
    "Wie organiseert de Olympische Spelen?",
    "Waar werden de Olympische Winterspelen 2006 gehouden?",
    "Door wie wordt Usain Bolt gecoacht?",
    "Wie traint Usain Bolt?",
    "Wie ontwierp het Beijing National Aquatics Center?",
    "Wie opende de Olympische Zomerspelen 2012?",
    "Hoe zwaar is Ranomi Kromowidjojo?",
    "Hoeveel deelnemers hadden de Olympische Zomerspelen van 2012?",
	"Wie heeft de Olympische Zomerspelen van 1936 geopend?",
	"Wanneer opende Adolf Hitler de Olympishe Spelen?",
	"Door wie zijn de Olympische Spelen van 1936 geopend?",
	"Hoeveel atleten namen deel aan de Olympische Zomerspelen van 2008?",
	"Hoeveel landen namen deel aan de Olympische Zomerspelen van 2008?",
	"Welke varianten heeft het meerkamp?",
	"Door wie werden de Olympische Spelen van 2004 geopend?",
	"Hoeveel bronzen medailles heeft Nederland op de Olympische Zomerspelen 2008?"
	]
