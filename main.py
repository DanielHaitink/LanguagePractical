#!/usr/bin/env python3
#environment set so that can use ./main.py
import sys, os.path
import variables as v
import traceback
from prePostParser import preParseSentence
from questionParser import isURI


# Format the answer the correct way
def formatAnswer(solutionID, solutionList):
	solutionString = str(solutionID) + "\t"

	# No solution
	if solutionList is None:
		v.printDebug("NO SOLUTION FOUND " + str(solutionID))
		return solutionString

	# Create string
	for item in solutionList:
		if isURI(item):
			item = item.replace("http://nl.dbpedia.org/resource/", "")
			item = item.replace("_", " ")
		solutionString += str(item) + "\t"
	return solutionString

# Stop the program and show an error of the missing file
def errorFileNotFound(fileName):
	sys.exit("FATAL ERROR: MISSING %s FILE, PLEASE MAKE SURE YOU HAVE THAT FILE IN THE RESOURCE FOLDER" %(fileName))

# Check if all needed files are located in the expected locations, if not exit program with an errorFileNotFound
def checkFilesExist():
	if not os.path.isfile("./" + v.FILE_NAMES):
		errorFileNotFound(v.FILE_NAMES)
	if not os.path.isfile("./" + v.FILE_SYNONYMS):
		errorFileNotFound(v.FILE_SYNONYMS)
	if not os.path.isfile("./" + v.FILE_PAIRCOUNT):
		errorFileNotFound(v.FILE_PAIRCOUNT)
	return

#Shows help
def showHelp():
	#TODO maybe add more?
	print("To exit the program type exit or use CTRL+D")
	input("PRESS THE ENTER KEY TO CONTINUE...")

# Print the example questions if in __DEBUG__ to stderror
def printExampleQuestions():
	n=1
	v.printDebug("Example questions: type a number to query this question")
	for q in v.QUESTIONS:
		v.printDebug(str(n) + ". " + q)
		n+=1

# First check for all needed files
checkFilesExist()

# set counter for solutionID
counter = 0
if v.__DEBUG__:
	printExampleQuestions()

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
	# If number is given without sentence, loof in the exampleQuestions
	if line.rstrip().isdigit():
		if int(line.rstrip()) > len(v.QUESTIONS):
			v.printDebug("Number too big!")
			continue
		line = str(line.rstrip()) + "\t" + str(v.QUESTIONS[int(line)-1])

	# See if a TAB is occuring, if so use the number before the TAB, else use counter
	if "\t" in line:
		lineList = line.split("\t")
		if len(lineList) == 2:
			solutionID = int(lineList[0])
			sentence = lineList[1].rstrip()
		else:
			v.printDebug("More than 2 tabs in sentence!")
			continue
	else:
		sentence = line.rstrip()

	# No sentence found or given
	if sentence is None or sentence is "":
		v.printDebug("No sentence given")
		continue

	# Go to preParse and wait for return
	try:
		solutionList = preParseSentence(sentence)

		# Print the answer
		print(formatAnswer(solutionID, solutionList))

	except Exception as e:
		print(solutionID)
		exc_type, exc_value, exc_tb = sys.exc_info()
		traceback.print_exception(exc_type, exc_value, exc_tb)

v.printDebug("Terminating Program!")
