from nltk.corpus import stopwords
import csv
from glob import glob
import ast

daten = glob("plenarprotokolle/testing_prep/*.xml.log")

sprecher_werte = {}
classifiers_neg, classifiers_pos = {}, {}
deutsche_stopwoerter = stopwords.words("german")


def collect_classifiers(sourcefile, target_dict):
    with open(sourcefile) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter="\t")
        line_count = 0
        for row in csv_reader:
            wert = float(row[1])
            formen = row[2].split(',')
            formen.append(row[0])
            # Wortart-Bezeichner vom Wort abtrennen:
            for form in formen:
                if '|' in form:
                    form = form.split('|')[0]
                target_dict[form.lower()] = wert
            line_count += 1


def drop_stopwoerter(protokoll):
    for i in range(len(protokoll)):
        rede = protokoll[i]
        for j in range(len(rede["inhalt"]["tokenisiert"])):
            absatz = rede["inhalt"]["tokenisiert"][j]
            rede["inhalt"]["tokenisiert"][j] = [wort for wort in absatz if wort not in deutsche_stopwoerter]
        protokoll[i] = rede
    return protokoll


def sentiment(input_text):
    score = 0
    postokens = 0
    negtokens = 0
    score_postokens = 0
    score_negtokens = 0
    for token in input_text:
        if token in classifiers_pos:
            postokens += 1
            score_postokens += classifiers_pos[token]
            score += classifiers_pos[token]
        if token in classifiers_neg:
            negtokens += 1
            score_negtokens -= classifiers_neg[token]
            score += classifiers_neg[token]
    return score/len(input_text)


collect_classifiers("SentiWS/SentiWS_v2.0_Negative.txt", classifiers_neg)
collect_classifiers("SentiWS/SentiWS_v2.0_Positive.txt", classifiers_pos)

for log in daten:
    protokoll_datei = open(log, "r+").read()
    protokoll_objekt = ast.literal_eval(protokoll_datei)
    protokoll_objekt = drop_stopwoerter(protokoll_objekt)
    breakpoint()
