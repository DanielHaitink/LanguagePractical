import sys
import variables as v
from prePostParser import preParseSentence

def formatAnswer(solutionID, solutionList):
	solutionString = str(solutionID) + "\t"
	if solutionList is None:
		v.printDebug("NO SOLUTION FOUND " + str(solutionID))
		return solutionString
	for item in solutionList:
		solutionString += str(item) + "\t"
	return solutionString




#Shows help
def showHelp():
	#TODO maybe add more?
	print("To exit the program type exit or use CTRL+D")
	input("PRESS THE ENTER KEY TO CONTINUE...")

counter = 0
for line in sys.stdin:
	counter += 1
	solutionID = counter
	sentence = None

	if line == "exit\n":
		break
	if line == "help\n":
		showHelp()
		continue

	if "\t" in line:
		lineList = line.split("\t")
		solutionID = int(lineList[0])
		sentence = lineList[1].rstrip()
	else:
		sentence = line.rstrip()
	if sentence is None:
		v.printDebug("No sentence given")
		continue

	solutionList = preParseSentence(line)
	print(formatAnswer(solutionID, solutionList))

	#Give sentence to prePostParse
v.printDebug("Terminating Program!")
