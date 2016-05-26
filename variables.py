import sys

__DEBUG__ = True

#Files
FILE_PAIRCOUNT = "pairCounts"
FILE_SYNONYMS = "synonyms"

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
WHD_NUMBER = ["hoeveel"]
WHD_OBJECT = ["welke"]


def printDebug(debug):
	if __DEBUG__:
		print(debug, file=sys.stderr)

def printError(debug, exception):
	if __DEBUG__:
		print(debug+ " " + exception, file=sys.stderr)
