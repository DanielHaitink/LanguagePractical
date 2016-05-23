import socket, sys
import variables as v
from lxml import etree


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
	alpinoXML = parseSentenceAlpino(sentence) 
	#determine what kind of sentence it is
	#send sentence to correct function in questionParser, then check if output is as expected
	#give both sentence as alpino xml, it only has to be parsed once (probably)
	return None
