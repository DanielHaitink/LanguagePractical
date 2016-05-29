import socket, sys
import variables as v
from lxml import etree
from questionParser import getTreeWordList, parseNumberOf, parseXofY

# return true is something from list is in sentence, else false
def containsFromList(sentence, list):
	for item in list:
		if item.lower() in sentence.lower():
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
#give both sentence as alpino xml, it only has to be parsed once (probably)
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
		#added debug statement, to see if we expect the right thing /anco
		v.printDebug("Expected type: " + str(expectedAnswer));

	# Check if question has expected answer number
	if expectedAnswer == v.ANSWER_NUMBER:
		solution = parseNumberOf(alpinoXML, v.ANSWER_NUMBER)
		if not solution is None:
			return solution

	# Check if question is of format X of Y
	wws = alpinoXML.xpath('//node[@pos="verb"]')

	if not listNoneCheck(wws):
		#anco : also true with: waar is sven kramer geboren:
		#if "zijn".lower() in getTreeWordList(wws[0], v.TYPE_LEMMA).lower(): #maybe add need of only 1 ww
		# my check from assignment 4:
		if(alpinoXML.xpath('//node[@stype="whquestion" and @root="ben" and @sc="copula" and ../../node[@pt="vnw"]]')):
			solution = parseXofY(alpinoXML, expectedAnswer)
			if not solution is None:
				return solution
		# TODO: ADD MORE PARSE TYPES
	return None
