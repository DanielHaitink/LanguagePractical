import sys
import variables as v
from prePostParser import preParseSentence


#Shows help
def showHelp():
	#TODO maybe add more?
	print("To exit the program type exit or use CTRL+D")
	input("PRESS THE ENTER KEY TO CONTINUE...")

for line in sys.stdin:
	if line == "exit\n":
		break
	if line == "help\n":
		showHelp()
		continue

	output = preParseSentence(line)
	if output is None:
		print("No solution found")
		#change to correct output
		continue
	print(output)

	#Give sentence to prePostParse

print("Terminating Program!", file=sys.stderr)
