from glob import glob
import spacy
import pickle
import re

daten = glob("plenarprotokolle/testing_prep/*.pickle")
satzzeichen = re.compile(r'.*[^a-zA-Z0-9\u0080-\u00FF#].*')
nlp = spacy.load("de_core_news_sm")


def tokenize_protokoll(objekt):

    reden = objekt["inhalt"]["reden"]

    for i in range(len(reden)):
        rede = reden[i]
        rede_tokenized = []
        for absatz in rede["inhalt"]["absaetze"]:
            absatz = nlp(absatz)
            absatz_tokenized = []
            for token in absatz:
                absatz_tokenized.append(token)
            rede_tokenized.append(absatz_tokenized)
        rede["inhalt"]["tokenisiert"] = rede_tokenized
        reden[i] = rede

    return reden


for log in daten:
    protokoll_datei = pickle.load(open(log, "rb"))
    protokoll_objekt = tokenize_protokoll(protokoll_objekt)
    with open(file=log, mode="w+") as outfile:
        pickle.dump(protokoll_objekt, outfile)
