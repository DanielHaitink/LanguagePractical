import socket, sys
import variables as v
from lxml import etree
from questionParser import getTreeWordList

def containsFromList(sentence, list):
	for item in list:
		if item in sentence:
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
	if v.__DEBUG__:
		print(bytes_received.decode('utf-8'), file=sys.stderr)
	xml = etree.fromstring(bytes_received)
	return xml

def preParseSentence(sentence):
	expectedAnswer = v.ANSWER_UNKNOWN

	alpinoXML = parseSentenceAlpino(sentence) 

	whds = alpinoXML.xpath('//node[@rel="whd"]')
	if whds == None or whds[0] == None:
		if __DEBUG__:
			print("ERROR: NO WHDS FOUND: "+ whds , file=sys.stderr)
			return None
	whd = getTreeWordList(whds[0], v.TYPE_WORD)

	if containsFromList(whd, v.WHD_LOCATION):
		expectedAnswer = v.ANSWER_LOCATION
	elif containsFromList(whd, v.WHD_PERSON):
		expectedAnswer = v.ANSWER_PERSON
	elif containsFromList(whd, v.WHD_NUMBER):
		expectedAnswer = v.ANSWER_NUMBER
	elif containsFromList(whd, v.WHD_DATE):
		expectedAnswer = v.ANSWER_DATE

	print(whd)


	#determine what kind of sentence it is
	#send sentence to correct function in questionParser, then check if output is as expected
	#give both sentence as alpino xml, it only has to be parsed once (probably)
	return None
