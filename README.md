# Sentimentanalyse von Plenarprotokollen der 19. Wahlperiode des deutschen Bundestags

## Entwicklungstagebuch

### Vorüberlegungen: XML-Parser
Die Protokolle liegen von Anfang an als XML-Dateien vor.
Eine zugehörige DTD spezifiziert und erläutert die Annotationen.
Nun sollen die Daten in Python eingelesen werden, um für die Sentimentanalyse weiterverarbeitet werden zu können.
Dazu muss zunächst ein taugliches Python-Paket gefunden werden, das eine XML-Schnittstelle bietet, damit keine fehleranfällige und langwierige Textverarbeitung von Grund auf programmiert werden muss.
Hier kommen vor allem drei Bibliotheken in Frage:
1. xml.ElementTree.etree
2. xml.dom.minidom
3. BeautifulSoup

Da es die angenehmste Art darstellt, mit XML-ähnlichen Daten zu arbeiten, wurde zunächst BeautifulSoup ausgewählt.
Ein weiteres Argument besteht darin, dass es zum Parsen das lxml-Paket nutzt, welches wiederum mit dem Ziel veröffentlicht wurde, das etree-Modul des Standard-xml-Paketes zu verbessern.
Die Auswahl des lxml-Backends zum Parsen, gewrappt in BeautifulSoup, funktionierte allerdings schon bald nicht mehr, weswegen auf das lxml-Paket selbst ausgewichen werden musste.
Um die üblichen 'pythonischen' Arbeitsgewohnheiten nicht ablegen zu müssen, bietet lxml als alternative Datenstrukturen Objekte an, die von Anfang an klarer verständlich sind.
Dazu wird statt dem etree-Modul das Modul objectify benutzt.

