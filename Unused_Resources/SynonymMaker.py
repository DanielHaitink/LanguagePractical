from OpenDutchWordnet import Wn_grid_parser


instance = Wn_grid_parser(Wn_grid_parser.odwn)
#instance.lemma_synonyms("paard")

words = []

for line in open("thesaurus.txt", 'r'):
    line = line.rstrip()
    line = line.split(";")
    for x in line:
        words.append(x)

for line in open("propEnter.txt", 'r'):
    if "nl.dbpedia" in line:
        line = line.rstrip()
        line = line.split("/")
        words.append(line[-1])

f = open('synonyms', 'w')

for word in set(words):
    synonyms = instance.lemma_synonyms(word)
    if len(synonyms)>1 and len(synonyms)<50: #only if there are synonyms
        for synonym in synonyms:
            f.write(synonym)
            f.write("#")
        f.write("\n")

f.close()
