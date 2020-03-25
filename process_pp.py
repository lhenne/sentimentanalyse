#### Pakete:
# lxml.objectify zum Parsen von XML mit transparenter Objektstruktur
# pickle zum permanenten Zwischenspeichern von Daten
# glob zum Einlesen der Daten aus Quellverzeichnis

from lxml import objectify as etree
import pickle
from glob import glob
from pprint import pprint

# XML-Dateien der Bundestagsprotokolle lokalisieren und Liste mit Adressen sammeln
daten = glob("plenarprotokolle/testing_prep/*.xml")
stammdaten_parse = etree.parse("plenarprotokolle/MDB_STAMMDATEN.XML")
mdbs_ohne_daten = {}

# Stammdaten der Sprecher einlesen
def get_partei(redner_id):
    mdb_id = stammdaten_parse.xpath(".//ID[text()=%s]" % redner_id)[0]
    mdb_daten = mdb_id.getparent()
    mdb_partei = mdb_daten.find("./BIOGRAFISCHE_ANGABEN/PARTEI_KURZ")[0]
    return mdb_partei

# Für jedes Protokoll die relevanten Informationen in einem Wörterbuch sammeln
for sitzung in daten:
    reden = []  # Liste aller Protokoll-Objekte
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

        # Leere Absaetze rausschmeissen
        for i in range(len(redetext)):
            absatz = redetext[i]
            if isinstance(absatz, str):
                pass
            else:
                absatz = absatz.text
                redetext[i] = absatz
        redetext = [x for x in redetext if x]

        kommentare = xml_rede.xpath("./kommentar")

        for i in range(len(kommentare)):
            kommentar = kommentare[i]
            if isinstance(kommentar, str):
                pass
            else:
                kommentar = kommentar.text
                kommentare[i] = kommentar

        redner_id = redner_info.xpath("@id")[0]

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
                "rede_id": xml_rede.xpath("@id")[0],
                "redner_id": redner_id,
                "redner_name": rednername,
                "redner_info": redner_info.find("./rolle/rolle_lang"),
                "redner_partei": redner_partei
            },
            "inhalt": {
                "absaetze": redetext,
                "kommentare": kommentare
            }
        }
        reden.append(rede)

    protokoll = {
        "meta": {
            "wahlperiode": metadata.find("./plenarprotokoll-nummer/wahlperiode"),
            "sitzungsnr": metadata.find("./sitzungstitel/sitzungsnr"),
            "ort": metadata.find("./veranstaltungsdaten/ort"),
            "datum": metadata.find("./veranstaltungsdaten/datum").get("date")
        },
        "inhalt": {
            "reden": reden
        }
    }

    with open(file=(sitzung + ".log"), mode="w+") as outfile:
        pprint(protokoll, stream=outfile)
    with open(file=(sitzung + ".pickle"), mode="wb") as outfile:
        pickle.dump(protokoll, outfile)
    pprint(mdbs_ohne_daten, stream=open("mdbs_ohne_daten.txt", "w+"))

breakPoint = "here"
