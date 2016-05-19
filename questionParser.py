import socket, re
from lxml import etree

def tree_yield(xml):
    #appends the value of the word-attribute for all nodes that are dominated by the node 'xml'
    #that is the argument of the function, and returns this a single string
    leaves = xml.xpath('descendant-or-self::node[@word]')
    words = []
    for l in leaves :
        words.append(l.attrib["lemma"])
    return " ".join(words)

# parse input sentence and return alpino output as an xml element tree
def alpino_parse(sent, host='zardoz.service.rug.nl', port=42424):
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
	#print(bytes_received.decode('utf-8'), file=sys.stderr)
	xml = etree.fromstring(bytes_received)
	return xml

#TODO: -for each type of question, add function to parse it
#- send parsed information to correct SPARQL query template
