#LanguagePractical

A Dutch question parser, which can answer your Dutch questions using dbPedia and local resources. 
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

The program will now accept the following input:
- `Hoe lang is Usain Bolt?`
- `1  Hoe lang is Usain Bolt?` (Note that it is a tab inbetween the number and sentence)

To exit the program type `exit` or use the key-combination `ctrl+D`

#TODO
- Vergelijkingsvragen (Grootste/Kleinste/Laatste/Eerste/Tweede/Derde[/Goud/Zilver/Brons])
- Uitbreiden PreParser (Wie opende de Olympische Zomerspelen 1936? / Wie heeft de olympische zomerspelen van 1936 geopend? )
- Hoe vragen (woorden als zwaar/lang etc.) --> ook preParser
- EVT uitbreiden synonyms
- Lijsten met antwoorden (Wie deden mee/Hoeveel deelnemers/Welke landen deden mee/etc.)
- in welke plaats is x geboren oid.
- andersom vragen: wie debuteerde op de OS 2012? OS 2012 heeft geen property debuteerde, maar mensen hebben wel property debuut die OS 2012 kan zijn.
