from pandas import read_csv
from glob import glob
import spacy
from spacy.tokens import DocBin

nlp = spacy.load("de_core_news_sm")

daten = glob("plenarprotokolle/pp19/*.xml.spacy")


spacy_db = {}
for datei in daten:
    protokoll = DocBin(store_user_data=True).from_bytes(open(datei, "rb").read())
    protokoll = list(protokoll.get_docs(nlp.vocab))
    datei = datei.split("plenarprotokolle/pp19/")[1]
        spacy_db[datei] = protokoll

for f, protokoll in spacy_db.items():
    for rede in protokoll:
        rede.user_data["entitaeten"] = [x.text for x in rede.ents]
        rede.user_data["entitaeten"] = [x for x in rede.user_data["entitaeten"] if not x == "||"]


def collect_classifiers_sentiws(sourcefile):
    with open(sourcefile) as csv_file:
        classifiers = read_csv(csv_file, sep="\t", header=None, names=["lemma", "wert", "formen"])
        classifiers["formen"] = classifiers["formen"].astype(str)
        classifiers["formen"] = classifiers["formen"].apply(lambda x: x.split(","))
        classifiers[["lemma", "pos"]] = classifiers["lemma"].str.split("|", expand=True)
        classifiers["lemma"] = classifiers["lemma"].astype(str)
        for formen, lemma in zip(classifiers.formen, classifiers.lemma):
            formen = formen.append(lemma)
        classifiers = classifiers.explode("formen")
    return classifiers


def collect_classifiers_gpc(sourcefile):
    with open(sourcefile) as csv_file:
        classifiers = read_csv(csv_file, sep="\t", header=None,
                               names=["form", "lemma", "pos", "polaritaet", "probabilitaet", "whatever"])
        classifiers = classifiers.drop(labels=["probabilitaet", "whatever"], axis=1)
    return classifiers


classifiers_neg_sentiws = collect_classifiers_sentiws("SentiWS/SentiWS_v2.0_Negative.txt")
classifiers_pos_sentiws = collect_classifiers_sentiws("SentiWS/SentiWS_v2.0_Positive.txt")

classifiers_neg_gpc = collect_classifiers_gpc("gpc/GermanPolarityClues-Negative-21042012.tsv")
classifiers_pos_gpc = collect_classifiers_gpc("gpc/GermanPolarityClues-Positive-21042012.tsv")


def sentiws_eval(text):
    sentiment_tokens = {}
    sentiment_score = 0
    for token in text.doc:
        if token.is_stop is not True:
            token_row = classifiers_neg_sentiws[classifiers_neg_sentiws.formen == token.text]
            if not token_row.empty:
                sentiment_tokens[token.text] = token_row["wert"].values[0]
                sentiment_score += token_row["wert"].values[0]
            else:
                token_row = classifiers_pos_sentiws[classifiers_pos_sentiws.formen == token.text]
                if not token_row.empty:
                    sentiment_tokens[token.text] = token_row["wert"].values[0]
                    sentiment_score += token_row["wert"].values[0]
    sentiment_tokens["sentiment_score"] = sentiment_score
    return sentiment_tokens


def gpc_eval(text):
    positive_token = []
    negative_token = []
    sentiment_tokens = {}
    for token in text.doc:
        if token.is_stop is not True:
            token_row = classifiers_neg_gpc[classifiers_neg_gpc.form == token.text]
            if not token_row.empty:
                negative_token.append(token.text)
            else:
                token_row = classifiers_pos_gpc[classifiers_pos_gpc.form == token.text]
                if not token_row.empty:
                    positive_token.append(token.text)
    sentiment_tokens["positiv"] = positive_token
    sentiment_tokens["negativ"] = negative_token
    return sentiment_tokens

counter = 0
for f, protokoll in spacy_db.items():
    counter += 1
    print(counter)
    for rede in protokoll:
        rede.user_data["sentiws"] = sentiws_eval(rede)
    for rede in protokoll:
        rede.user_data["gpc"] = gpc_eval(rede)
    doc_bin = DocBin(
        attrs=["POS", "TAG", "LEMMA", "IS_STOP", "DEP", "SHAPE", "ENT_ID", "ENT_IOB", "ENT_KB_ID", "ENT_TYPE"],
        store_user_data=True)
    for doc in protokoll:
        doc_bin.add(doc)
    spacy_out = doc_bin.to_bytes()
    with open(file=("plenarprotokolle/pp19/" + f + ".sentiment"), mode="wb") as spacy_outfile:
        spacy_outfile.write(spacy_out)



