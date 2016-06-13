#PAM - LanguagePractical

PAM is a Dutch question parser, which can answer your Dutch questions using DBPedia and local resources found in the `Resources` map.
It is mainly focussed on questions about the Olympics.

##Prerequisites
This program is dependent on multiple python libraries:
- lxml
- SPARQLWrapper

Make sure you have these installed, this can be done using the following commands:
- `pip install lxml`
- `pip install SPARQLWrapper`

Also make sure you download the file called `pairCounts` over [here](http://spotlight.sztaki.hu/downloads/latest_data/nl.tar.gz) and make sure you place it in the `Resources` map.

Furthermore, do NOT delete files from the `Resources` map as they are vital for our program. The program *does not work* if the files are misplaced or removed.

##Usage

Use the program by opening a terminal window. Go to the map the python files are in and there do the following:
`python3 main.py`

To feed it a file with questions formatted like the questions below you can do the following:
`python3 main.py < ./Questions/QuestionsFile.txt > ./Questions/OutputFile.txt`
Running big files of questions takes quite some time.

The program accepts Dutch questions, formatted like the following input:
- `Hoe lang is Usain Bolt?`
- `1  Hoe lang is Usain Bolt?` (Note that it is a tab in between the number and sentence)

The program will have the output of a number followed by a tab and then the solution found.
The Number is either the number you have given as input (before the tab), or the iteration number the input check is in.
An example is shown below:
`1	1,96 m`

To exit the program type `exit` or use the key-combination `ctrl+D`

###Debug

If the program prints all debug statements while this is not wanted, please edit the `__DEBUG__` variable in `variables.py` to `False`.
