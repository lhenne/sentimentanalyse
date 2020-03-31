#### Pakete:
# lxml.objectify zum Parsen von XML mit transparenter Objektstruktur
# pickle zum permanenten Zwischenspeichern von Daten
# glob zum Einlesen der Daten aus Quellverzeichnis

from lxml import objectify as etree
import pickle
from glob import glob
from pprint import pprint
import spacy
from spacy.tokens import DocBin

# XML-Dateien der Bundestagsprotokolle lokalisieren und Liste mit Adressen sammeln
daten = glob("plenarprotokolle/pp19/*.xml")
total = len(daten)
current = 1

stammdaten_parse = etree.parse("plenarprotokolle/MDB_STAMMDATEN.XML")
mdbs_ohne_daten = {}
nlp = spacy.load("de_core_news_sm")

# Stammdaten der Sprecher einlesen
def get_partei(redner_id):
    mdb_id = stammdaten_parse.xpath(".//ID[text()=%s]" % redner_id)[0]
    mdb_daten = mdb_id.getparent()
    mdb_partei = mdb_daten.find("./BIOGRAFISCHE_ANGABEN/PARTEI_KURZ")[0].text
    return mdb_partei

# Für jedes Protokoll die relevanten Informationen in einem Wörterbuch sammeln
for sitzung in daten:
    print("[" , current , "/" , total , "]")
    reden = []  # Liste aller Protokoll-Objekte
    spacy_reden = []
    redetext_klassen = ["J_1", "J", "O", "A_TOP", "T_Beratung", "T_Drs", "T_E_Drs", "T_E_E_Drs", "T_E_fett",
    "T_NaS", "T_NaS_NaS", "T_ZP_NaS", "T_ZP_NaS_NaS", "T_ZP_NaS_NaS_Strich",
    "T_Ueberweisung", "T_fett", "T_ohne_NaS"]  # relevante Annotationsklassen für Redetext
    redetext_kondition = "./p[@klasse='" + "' or @klasse='".join(redetext_klassen) + "']"

    pp_parse = etree.parse(sitzung)  # Sitzungsprotokoll parsen
    metadata = pp_parse.find(".//kopfdaten")  # Metadaten einlesen
    xml_reden = pp_parse.findall(".//rede")  # Reden einlesen

    for xml_rede in xml_reden:
        redner_info = xml_rede.find("./p[@klasse='redner']/redner")
        redetext = xml_rede.xpath(redetext_kondition)
        redetext_tokenized = []
        # Leere Absaetze rausschmeissen
        for i in range(len(redetext)):
            absatz = redetext[i]
            if isinstance(absatz, str):
                pass
            else:
                absatz = absatz.text
                redetext[i] = absatz
        redetext = [x for x in redetext if x]
        redetext_tokenized = " || ".join(redetext)
        redetext_tokenized = nlp(redetext_tokenized)

        kommentare = xml_rede.xpath("./kommentar")

        for i in range(len(kommentare)):
            kommentar = kommentare[i]
            if isinstance(kommentar, str):
                pass
            else:
                kommentar = kommentar.text
                kommentare[i] = kommentar

        redner_id = str(redner_info.xpath("@id")[0])

        try:
            rednername = redner_info.find("./name/vorname") + " " + redner_info.find("./name/nachname")
        except:
            try:
                rednername = redner_info.find("./name/nachname")
            except:
                try:
                    rednername = redner_info.find("./name/vorname")
                except:
                    print("Rednername in Datei", sitzung, "nicht auffindbar.")

        try:
            redner_partei = get_partei(redner_id)
        except:
            print("Sitzung", metadata.find("./sitzungstitel/sitzungsnr"), ": Keine Informationen zu Redner", rednername, "mit ID", redner_id, "verfügbar.")
            mdbs_ohne_daten[rednername] = redner_id
            redner_partei = 'Unbekannt'

        rede = {
            "meta": {
                "rede_id": str(xml_rede.xpath("@id")[0]),
                "redner_id": redner_id,
                "redner_name": rednername,
                "redner_info": str(redner_info.xpath("./rolle/rolle_lang")),
                "redner_partei": redner_partei
            },
            "inhalt": {
                "absaetze": redetext,
                "kommentare": kommentare
            }
        }
        reden.append(rede)
        spacy_reden.append(redetext_tokenized)

    protokoll = {
        "meta": {
            "wahlperiode": metadata.find("./plenarprotokoll-nummer/wahlperiode").text,
            "sitzungsnr": metadata.find("./sitzungstitel/sitzungsnr").text,
            "ort": metadata.find("./veranstaltungsdaten/ort").text,
            "datum": metadata.find("./veranstaltungsdaten/datum").get("date")
        },
        "inhalt": {
            "reden": reden
        }
    }

    # with open(file=(sitzung + ".log"), mode="w+") as outfile:
    #    pprint(protokoll, stream=outfile)
    # with open(file=(sitzung + ".pickle"), mode="wb") as outfile:
    #     pickle.dump(protokoll, outfile)
    pprint(mdbs_ohne_daten, stream=open("mdbs_ohne_daten.txt", "w+"))

    doc_bin = DocBin(attrs=["POS", "TAG", "LEMMA", "IS_STOP", "DEP", "SHAPE"], store_user_data=True)
    for doc in spacy_reden:
        doc_bin.add(doc)
    spacy_out = doc_bin.to_bytes()
    with open(file=(sitzung + ".spacy"), mode="wb") as spacy_outfile:
        spacy_outfile.write(spacy_out)

    current += 1

breakPoint = "here"
