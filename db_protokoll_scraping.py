"""This is a data scraper for the crawling and searching of child care facilities in the canton of Zürich, Switzerland, from the website http://www.lotse.zh.ch. Code: Jan Rothenberger, CC 2.0 BY NC"""

import os
import sys
import bundestag_protokolle_xlsx
import re  # reguläre Ausdrücke, brauchen wir später
from bs4 import BeautifulSoup  # BeautifulSoup: unser Werkzeug der Wahl
import urllib.request

webliste = []  # Liste mit den zu scrapenden URLs, Typen
webliste.append(("kita", "http://www.lotse.zh.ch/service/detail/500076/from/service?q=kinderbetreuung&amp;qID=k500502"))
webliste.append(("kihu", "http://www.lotse.zh.ch/service/detail/500101/from/service?q=kinderbetreuung&amp;qID=k500502"))
webliste.append(("mita", "http://www.lotse.zh.ch/service/detail/500078/from/service?q=kinderbetreuung&amp;qID=k500502"))
webliste.append(("hort", "http://www.lotse.zh.ch/service/detail/500077/from/service?q=kinderbetreuung&amp;qID=k500502"))


def lotse_scrapen():
    alles = []
    zeile = ""
    for unterseite in webliste:  # läuft die kategorieseiten in der webliste ab und wendet datenholen darauf an
        Typ_angebot = unterseite[0]
        seite = urllib.request.urlopen(unterseite[1])
        alles.extend(datenholen(seite, Typ_angebot))

    typen = {"kita": "Kinderkrippen oder Kindertagesstätte", "kihu": "Kinderhütedienst", "mita": "Mittagstisch",
             "hort": "Hort"}
    f = open("datadump.csv", 'wt', newline='\n')
    try:
        fieldnames = ['type', 'name', 'contact', 'address', 'tel', 'web', 'infos']
        writer = bundestag_protokolle_xlsx.DictWriter(f, fieldnames=fieldnames, delimiter=';', extrasaction='raise')
        writer.writerow({fn: fn for fn in fieldnames})
        for entry in alles:
            try:
                writer.writerow(entry)
            except:
                print(entry)
    finally:
        f.close()
        # print open(sys.argv[1], 'rt').read()


def datenholen(response, typ_Angebot):  # nimmt kategorieseite und typ, gibt listenabschnitt mit einträgen zurück
    datensatz = []  # dictionary-liste, wird gefüllt und zurückgegeben
    eintraege = []  # webadressen, die von der unterfunktion gescrapet werden
    listen_soup = BeautifulSoup(response)
    results = listen_soup.findAll('a', attrs={'class': 'mehr'})  # links der Klasse "mehr" finden
    for result in results:
        eintraege.append(result['href'])  # link-url in liste eintragen

    y = 0
    for eintrag in eintraege:  # unterfunktion auf elementen der url-liste aufrufen
        datensatz.append(eintrag_machen(("http://www.lotse.zh.ch" + eintrag), typ_Angebot))
    return datensatz


def eintrag_machen(eintrag, typ_angebot):
    entry = {}
    entry['type'] = ""
    entry['type'] = typ_angebot
    entry['name'] = ""
    entry['contact'] = ""
    entry['address'] = ""
    entry['tel'] = ""
    entry['web'] = ""
    entry['infos'] = ""

    try:
        page = urllib.request.urlopen(eintrag)
        soup = BeautifulSoup(page)
        entry['name'] = soup.b.string
        liste = [word.strip() for word in soup.b.string.find_all_next(text=True)]  # von \n gesäuberte Liste
        while '' in liste:
            liste.remove('')  # alle leere Elemente (strings) werden entfernt

        i = 0  # schluss abschneiden
        for teil in liste:
            if teil == "Zurück" or teil == "#BeginCopy'":
                del liste[i:]  # schneidet nach i ab, vor "Zurück"
                break
            else:
                i = i + 1
        for teil in liste:  # Tel und URLs hinzufügen
            if teil.startswith("Tel."):
                entry['tel'] = teil
            elif teil.startswith("www.") or teil.startswith("www."):
                entry['web'] = teil
            elif teil.startswith("var"):
                liste.remove(teil)

        i = 0
        while ((not re.search(r"[0-9]", liste[i])) and (not liste[i].endswith("strasse"))):
            entry['contact'] = liste[i] + " " + entry['contact']
            i = i + 1
        try:
            entry['address'] = liste[i]  # zusätzliche Adressoder PLZ hinzufügen
            plz = (re.search(r"^[0-9]{4} [A-Za-z]*", liste[i]))  # 4-stellige Zahl im Listeneintrag finden
            if not plz:  # plz nicht auf dieser zeile
                if re.search(r"^[0-9]{4} [A-Za-z]*", liste[i + 1]):  # plz ist auf der folgezeile
                    entry['address'] = entry['address'] + ", " + liste[
                        i + 1]  # Noch nicht PLZ, weitere Adresszeile, darum PLZ hinzufügen
                else:
                    return False  # keine plz gefunden, kein mapping möglich -&gt; abbruch
        except:
            print("an der url-geschichte liegts")

        i = 1  # anfang abschneiden
        for teil in liste:
            if teil.startswith("Lageplan") or teil.startswith("Informationen"):
                del liste[:i]  # schneidet mit i ab, nach "Lageplan"
            else:
                i = i + 1

        entry['infos'] = ",".join(liste)
        return entry

    except:
        print("doof, das")
        return False

lotse_scrapen()