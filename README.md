#PAM - LanguagePractical

PAM is a Dutch question parser, which can answer your Dutch questions using dbPedia and local resources.
Mainly focussed on questions about the Olympics.

##Prerequisites
This program is dependent on multiple python libraries:
- lxml
- SPARQLWrapper

Make sure you have these installed, this can be done using the following commands:
- `pip install lxml`
- `pip install SPARQLWrapper`

Also make sure you download the file called `pairCounts` over [here](http://spotlight.sztaki.hu/downloads/latest_data/nl.tar.gz) and make sure you place it in the `Resources` map

##Usage

Use the program by opening a terminal window. Go to the map the python files are in and there do the following:

`python3 main.py`

To feed it a file with questions formatted like the questions below you can do the following:

`python3 main.py < ./QuestionsFile.txt > ./OutputFile.txt`

The program accepts Dutch questions, formatted like the following input:
- `Hoe lang is Usain Bolt?`
- `1  Hoe lang is Usain Bolt?` (Note that it is a tab in between the number and sentence)

To exit the program type `exit` or use the key-combination `ctrl+D`
