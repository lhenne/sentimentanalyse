from nltk.tokenize import word_tokenize
from glob import glob
import ast

daten = glob("plenarprotokolle/pp19/*.xml.log")

classifiers_neg, classifiers_pos = {}, {}



for protokoll_log in daten:
    protokoll = open(protokoll_log, "r+").read()
    protokoll = ast.literal_eval(protokoll)

    for rede in protokoll["inhalt"]["reden"]:
        redetext_tokenized = []
        for absatz in rede["inhalt"]["absaetze"]:
            absatz_tokenized = word_tokenize(absatz, language="german")
            redetext_tokenized.append(absatz_tokenized)


