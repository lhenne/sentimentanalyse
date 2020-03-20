#### Pakete:
# lxml.objectify zum Parsen von XML mit transparenter Objektstruktur
# pickle zum permanenten Zwischenspeichern von Daten
# glob zum Einlesen der Daten aus Quellverzeichnis

from lxml import objectify as etree
import pickle
from glob import glob

# XML-Dateien der Bundestagsprotokolle lokalisieren und Liste mit Adressen sammeln
daten = glob("plenarprotokolle/pp19/*.xml")

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
        kommentare = xml_rede.xpath("./kommentar")
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

        rede = {
            "meta": {
                "rede_id": xml_rede.xpath("@id")[0],
                "redner_id": redner_info.xpath("@id")[0],
                "redner_name": rednername,
                "redner_info": redner_info.find("./rolle/rolle_lang")
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

    with open(file=(sitzung + ".pickle"), mode="wb") as outfile:
        pickle.dump(protokoll, outfile)

breakPoint = "here"
