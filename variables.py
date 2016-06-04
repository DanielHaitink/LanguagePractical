import sys

__DEBUG__ = False

#Files
FILE_PAIRCOUNT = "pairCounts"
FILE_SYNONYMS = "synonyms"
FILE_NAMES = "names.txt"

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
WHD_PERSON = ["wie"]
WHD_DATE = ["wanneer"]
WHD_NUMBER = ["hoeveel", "hoe"]
WHD_OBJECT = ["welke"]

PASS_PERSON = ["sir", "madam", "Dame", "lord", "Lady", "Queen"]

#dataTypes
DATATYPE_INTEGER = "http://www.w3.org/2001/XMLSchema#integer"
DATATYPE_DATE = "http://www.w3.org/2001/XMLSchema#date"
DATATYPE_STRING = "http://www.w3.org/2001/XMLSchema#string"
DATATYPE_MONTHDAY = "http://www.w3.org/2001/XMLSchema#gMonthDay"


def printDebug(debug):
	if __DEBUG__:
		print(debug, file=sys.stderr)

def printError(debug, exception):
	if __DEBUG__:
		print(debug+ " " + exception, file=sys.stderr)

#variables used to extract all given properties from sentences.. can be removed later on
prop = ""
sentence = ""
nr = -1
properties = []
