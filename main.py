#!/usr/bin/env python3
#environment set so that can use ./main.py
import sys, os.path
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

def errorFileNotFound(fileName):
	sys.exit("FATAL ERROR: MISSING %s FILE, PLEASE MAKE SURE YOU HAVE THAT FILE IN THE RESOURCE FOLDER" %(fileName))

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

def printExampleQuestions():
	n=1
	print ("Example questions: type a number to query this question")
	for q in v.QUESTIONS:
		print (str(n) + ". " + q)
		n+=1

checkFilesExist()

# set counter for solutionID
counter = 0
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

	if line.rstrip().isdigit():
		line = str(line.rstrip()) + "\t" + str(v.QUESTIONS[int(line)-1])

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
	solutionList = preParseSentence(sentence)

	# Print the answer
	print(formatAnswer(solutionID, solutionList))
v.printDebug("Terminating Program!")
