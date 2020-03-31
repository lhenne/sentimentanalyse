from glob import glob
import spacy
import pickle
import re

daten = glob("plenarprotokolle/pp19/*.pickle")
satzzeichen = re.compile(r'.*[^a-zA-Z0-9\u0080-\u00FF#].*')



def tokenize_protokoll(objekt):

    reden = objekt["inhalt"]["reden"]

    for i in range(len(reden)):
        rede = reden[i]
        rede_tokenized = []
        for absatz in rede["inhalt"]["absaetze"]:
            absatz_tokenized = nlp(absatz)
            rede_tokenized.append(absatz_tokenized)
        rede["inhalt"]["tokenisiert"] = rede_tokenized
        reden[i] = rede

    return reden


for log in daten:
    protokoll_datei = pickle.load(open(log, "rb"))
    protokoll_objekt = tokenize_protokoll(protokoll_datei)
    with open(file=log, mode="wb") as outfile:
        pickle.dump(protokoll_objekt, outfile)
