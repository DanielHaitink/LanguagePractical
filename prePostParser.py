import socket, sys
import variables as v
from lxml import etree
from questionParser import getTreeWordList, parseNumberOf, parseXofY, parseWhereWhen, parseHow, parseVerbs

# return true is something from list is in sentence, else false
def containsFromList(sentence, list):
	for item in list:
		if sentence.lower().startswith(item.lower()):
			return True
	return False

# parse input sentence and return alpino output as an xml element tree
def parseSentenceAlpino(sent, host='zardoz.service.rug.nl', port=42424):
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.connect((host,port))
	sent = sent + "\n\n"
	sentbytes= sent.encode('utf-8')
	s.sendall(sentbytes)
	bytes_received= b''
	while True:
		byte = s.recv(8192)
		if not byte:
			break
		bytes_received += byte
	v.printDebug(bytes_received.decode('utf-8'))
	xml = etree.fromstring(bytes_received)
	return xml

# check if list is None or first location in list is none
def listNoneCheck(list):
	if list == None or list == [] or list[0] == None:
		return True
	return False

#determine what kind of sentence it is
#send sentence to correct function in questionParser, then check if output is as expected
def preParseSentence(sentence):
	expectedAnswer = v.ANSWER_UNKNOWN
	solution = None

	alpinoXML = parseSentenceAlpino(sentence)

	# Parse the WHD of the sentence in alpino
	whds = alpinoXML.xpath('//node[@rel="whd"]')
	if listNoneCheck(whds):
		v.printDebug("ERROR: NO WHDS FOUND: "+ str(whds))
	else:
		whd = getTreeWordList(whds[0], v.TYPE_WORD)

		# Check what expectedAnswer is based on WHD, if not recognized it is v.ANSWER_UNKNOWN
		if containsFromList(whd, v.WHD_LOCATION):
			expectedAnswer = v.ANSWER_LOCATION
		elif containsFromList(whd, v.WHD_PERSON):
			expectedAnswer = v.ANSWER_PERSON
		elif containsFromList(whd, v.WHD_NUMBER):
			expectedAnswer = v.ANSWER_NUMBER
		elif containsFromList(whd, v.WHD_OBJECT):
			expectedAnswer = v.ANSWER_OBJECT
		elif containsFromList(whd, v.WHD_DATE):
			expectedAnswer = v.ANSWER_DATE
		v.printDebug("Expected type: " + str(expectedAnswer));

# Look for the correct function to parse the sentence
	# Check if question has expected answer number
	if expectedAnswer == v.ANSWER_NUMBER:
		v.printDebug("Parsing as a number of question")
		solution = parseNumberOf(alpinoXML, v.ANSWER_NUMBER, sentence)
		if not solution is None:
			return solution

	# Check if question is of format X of Y
	wws = alpinoXML.xpath('//node[@pos="verb"]')

	#check different possibilities and parse them accordingly
	if not listNoneCheck(wws):
		words = sentence.split(" ")
		if (len(words)>1):

			if(words[0]=="Welke" or (words[0]=="Aan" and words[1]=="welke")):
				v.printDebug("Parsing as a welke question")
				solution = parseXofY(alpinoXML, expectedAnswer, sentence)
				if not solution is None:
					return solution

			if(words[0]=="Door"):
				v.printDebug("Parsing as a door wie question")
				solution = parseVerbs(alpinoXML, expectedAnswer, sentence)
				if not solution is None:
					return solution

		if(alpinoXML.xpath('//node[@stype="whquestion" and @root="ben" and @sc="copula" and ../../node[@pt="vnw"]]')):
			v.printDebug("Parsing as a X of Y question")
			solution = parseXofY(alpinoXML, expectedAnswer, sentence)
			if not solution is None:
				return solution

		if(alpinoXML.xpath('//node[@rel="whd" and @cat="ap"]')):
			v.printDebug("Parsing as a how question")
			solution = parseHow(alpinoXML, expectedAnswer, sentence)
			if not solution is None:
				return solution

		if(alpinoXML.xpath('//node[@rel="whd" and (@frame="er_wh_loc_adverb" or @frame="wh_tmp_adverb")]')):
			v.printDebug("Parsing as a where/when question")
			solution = parseWhereWhen(alpinoXML, expectedAnswer, sentence)
			if not solution is None:
				return solution

		if(alpinoXML.xpath('//node[@rel="su" and ../@rel="body" and @index and not(@cat)]') and not sentence.split(" ")[0]=="Hoeveel"):
			v.printDebug("Parsing as a verbs question")
			solution = parseVerbs(alpinoXML, expectedAnswer, sentence)
			if not solution is None:
				return solution

		v.printDebug("Final Try in parseXofY")

		# Final try to at least find something
		return(parseXofY(alpinoXML, expectedAnswer, sentence))

	return None
