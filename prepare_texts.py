from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from glob import glob
import ast
import csv
import re

daten = glob("plenarprotokolle/testing_prep/19001-data.xml.log")

classifiers_neg, classifiers_pos = {}, {}
deutsche_stopwoerter = stopwords.words("german")
with open("SentiWS/SentiWS_v2.0_Negative.txt") as csv_file:
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
            classifiers_neg[form.lower()] = wert

        line_count += 1

with open("SentiWS/SentiWS_v2.0_Positive.txt") as csv_file:
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
            classifiers_pos[form.lower()] = wert

        line_count += 1

def sentiment(input):
    score = 0
    postokens = 0
    negtokens = 0
    score_postokens = 0
    score_negtokens = 0
    for token in input:
        if token in classifiers_pos:
            postokens += 1
            score_postokens += classifiers_pos[token]
            score += classifiers_pos[token]
        if token in classifiers_neg:
            negtokens += 1
            score_negtokens -= classifiers_neg[token]
            score += classifiers_neg[token]
    return score
    # return {'text':' '.join(input),'score':score,'postokens':postokens,'negtokens':negtokens,'positive_score':score_postokens,'negative_score':score_negtokens,'date':tweet['datum']}


for protokoll_log in daten:
    protokoll = open(protokoll_log, "r+").read()
    protokoll = ast.literal_eval(protokoll)

    for rede in protokoll["inhalt"]["reden"]:
        sentiment_summe = 0
        redetext_tokenized = []
        for absatz in rede["inhalt"]["absaetze"]:
            absatz_tokenized = word_tokenize(absatz, language="german")

            for i in range(len(absatz_tokenized)):
                absatz_tokenized[i] = absatz_tokenized[i].lower()

            absatz_tokenized = [wort for wort in absatz_tokenized if wort not in deutsche_stopwoerter]

            satzzeichen = re.compile(r'.*[^a-zA-Z0-9\u0080-\u00FF#].*')
            absatz_tokenized = [x for x in absatz_tokenized if not satzzeichen.match(x)]

            redetext_tokenized.append(absatz_tokenized)
        for absatz_tokenized in redetext_tokenized:
            sentiment_summe += sentiment(absatz_tokenized)
        print(sentiment_summe)

