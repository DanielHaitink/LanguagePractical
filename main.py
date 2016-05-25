import sys
import variables as v
from prePostParser import preParseSentence

# Format the answer the correct way
def formatAnswer(solutionID, solutionList):
	solutionString = str(solutionID) + "\t"

	# No solution
	if solutionList is None:
		v.printDebug("NO SOLUTION FOUND " + str(solutionID))
		return solutionString

	# Create string
	for item in solutionList:
		solutionString += str(item) + "\t"
	return solutionString

#Shows help
def showHelp():
	#TODO maybe add more?
	print("To exit the program type exit or use CTRL+D")
	input("PRESS THE ENTER KEY TO CONTINUE...")

# set counter for solutionID
counter = 0
for line in sys.stdin:
	# Default vars
	counter += 1
	solutionID = counter
	sentence = None

	# look for keywords
	if line == "exit\n":
		break
	if line == "help\n":
		showHelp()
		continue

	# See if a TAB is occuring, if so use the number before the TAB, else use counter
	if "\t" in line:
		lineList = line.split("\t")
		solutionID = int(lineList[0])
		sentence = lineList[1].rstrip()
	else:
		sentence = line.rstrip()

	# No sentence found or given
	if sentence is None or sentence is "":
		v.printDebug("No sentence given")
		continue

	# Go to preParse and wait for return
	solutionList = preParseSentence(line)

	# Print the answer
	print(formatAnswer(solutionID, solutionList))
v.printDebug("Terminating Program!")
