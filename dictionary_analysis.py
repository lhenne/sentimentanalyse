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
        rede["inhalt"]["tokenisiert_voll"] = [x for x in rede["inhalt"]["tokenisiert"]]
        for j in range(len(rede["inhalt"]["tokenisiert"])):
            absatz = rede["inhalt"]["tokenisiert"][j]
            rede["inhalt"]["tokenisiert"][j] = [wort for wort in absatz if wort not in deutsche_stopwoerter]
        protokoll[i] = rede
    return protokoll


def analyse(log):
    protokoll_datei = open(log, "r+").read()
    protokoll_objekt = drop_stopwoerter(ast.literal_eval(protokoll_datei))

    for i in range(len(protokoll_objekt)):
        rede_tokenisiert = protokoll_objekt[i]["inhalt"]["tokenisiert"]
        rede_tokenisiert_voll = protokoll_objekt[i]["inhalt"]["tokenisiert_voll"]
        protokoll_objekt[i]["meta"]["sentimentwerte"] = []
        protokoll_objekt[i]["meta"]["wortanzahl"] = []
        for j in range(len(rede_tokenisiert)):
            absatz = rede_tokenisiert[j]
            scores_dict = {}
            for wort in absatz:
                scores_dict[wort] = token_sentiment(wort)
            absatz = scores_dict
            rede_tokenisiert[j] = absatz
            protokoll_objekt[i]["meta"]["sentimentwerte"].append(sum(absatz.values()))
            protokoll_objekt[i]["meta"]["wortanzahl"].append(len(rede_tokenisiert_voll[j]))
        protokoll_objekt[i]["inhalt"]["tokenisiert"] = rede_tokenisiert
    return protokoll_objekt


def token_sentiment(token):
    score = 0
    if token in classifiers_pos:
        score = classifiers_pos[token]
    elif token in classifiers_neg:
        score = classifiers_neg[token]
    return score


collect_classifiers("SentiWS/SentiWS_v2.0_Negative.txt", classifiers_neg)
collect_classifiers("SentiWS/SentiWS_v2.0_Positive.txt", classifiers_pos)

for datei in daten:
    datei_mit_werten = analyse(datei)

