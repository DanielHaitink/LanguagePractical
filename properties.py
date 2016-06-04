#!/usr/bin/env python3
import sys
import variables as v
from prePostParser import preParseSentence


def initSentence():
	v.sentence = ""
	v.nr = -1
	v.prop = " "
	v.GETONLYPROPERTIES = True

def setSetence(s):
	v.sentence = s;


def setNr(n):
	v.nr= n

def setProp(p):
	v.prop = p

def getKey(item):
	return len(item[1])

def insertProperty():
	for p in v.properties:
		print(p[0])
		if p[0] == v.prop:
			p[1].append(str(v.nr)+" "+str(v.sentence))
			return
	v.properties.append([v.prop, [(str(v.nr)+" "+str(v.sentence))]])

def printProperties():
	

	prop = sorted(v.properties, key=getKey, reverse=True)
	for p in prop:
		sen = ""
		for s in p[1]:
			sen = sen + " " + s
		print(str(getKey(p))+ " "+str(p[0]) + " " + sen)




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
	initSentence()

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
		setNr(solutionID)
		sentence = lineList[1].rstrip()
	else:
		sentence = line.rstrip()

		# No sentence found or given
	if sentence is None or sentence is "":
		v.printDebug("No sentence given")
		continue

	setSetence(sentence)
	# Go to preParse and wait for return
	solutionList = preParseSentence(line)
	insertProperty()


printProperties()

	# Print the answer
	#print(formatAnswer(solutionID, solutionList))
#v.printDebug("Terminating Program!")
