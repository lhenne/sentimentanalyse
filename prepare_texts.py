from nltk.tokenize import word_tokenize
from glob import glob
from pprint import pprint
import ast
import re

daten = glob("plenarprotokolle/testing_prep/*.xml.log")


def tokenize_protokoll(objekt):
    reden = objekt["inhalt"]["reden"]
    satzzeichen = re.compile(r'.*[^a-zA-Z0-9\u0080-\u00FF#].*')

    for i in range(len(reden)):
        rede = reden[i]
        rede_tokenized = []

        for absatz in rede["inhalt"]["absaetze"]:
            absatz_tokenized = word_tokenize(absatz, language="german")
            absatz_tokenized = [x.lower() for x in absatz_tokenized if not satzzeichen.match(x)]
            rede_tokenized.append(absatz_tokenized)
        rede["inhalt"]["tokenisiert"] = rede_tokenized

        reden[i] = rede

    return reden


for log in daten:
    protokoll_datei = open(log, "r+").read()
    protokoll_objekt = ast.literal_eval(protokoll_datei)
    protokoll_objekt = tokenize_protokoll(protokoll_objekt)
    with open(file=log, mode="w+") as outfile:
        pprint(protokoll_objekt, stream=outfile)
