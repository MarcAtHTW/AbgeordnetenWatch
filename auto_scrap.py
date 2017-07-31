from nltk import FreqDist
from nltk.corpus import stopwords
import operator
from nltk import sent_tokenize, word_tokenize
import os
#import wget
from os import remove
from selenium import webdriver
from bs4 import BeautifulSoup
import xlsxwriter
import re
import codecs
import urllib.request, json
import pickle
import time
import xlrd
import csv
import collections
import progressbar
import json
from time import sleep

os.environ['JAVAHOME'] = "C:/Program Files/Java/jdk1.8.0_20/bin/java.exe"

''' Globals '''
indexierte_liste                = []  # Vorhalten von Redeteilen
start_Element_Rede              = 0
list_with_startelement_numbers  = []  # enthält Start item aller Redetexte
list_with_startEnd_numbers      = []  # enthält Start und Ende item aller Redetexte
liste_mit_Endnummern            = []
number_of_last_element          = 0
list_elements_till_first_speech = []  # enthält listenelemente bis zur ersten Rede
politican_name                  = ""
party_name                      = ""
liste_zeilen                    = []
isMatcherAndNameGefunden        = False
isMatchergefunden               = False
isNameGefunden                  = False
zeitstrahl_counter              = 0
temp_counter                    = 0
result_index                    = 0
counter_string                  = 1
redner_zaehler_fuer_iteration_durch_alle_redner = 0
aktuelle_sitzungsnummer         = ''
deleted_speechers_in_analyse_content = []
liste_zeilen_einer_sitzung      = []
ergebniszusammenfassung= {}

'''Globals fuer Excelsheet'''
row_sitzungsdaten = 1
row_topdaten = 1
row_redner_rede = 1
row_beifalltext = 1
beifall_id_row = 1
temp_row_beifalltext = 1
row_beifalldaten = 1
t_row = 1
temp_row_beifalldaten = 1
row_wortmeldedaten = 1
temp_row_wortmeldedaten = 1
row_seldom_words_daten = 1
temp_row_seldom_words_daten = 1
t_row = 1
row_freq_words_daten = 1
temp_row_freq_words_daten = 1
t_row_freq_words_daten = 1
temp_row_beifalldaten_text = 1
count_deleted_tops = 0


workbook = xlsxwriter.Workbook('bundestag_protokolle.xlsx')
sitzungsdaten = workbook.add_worksheet('Sitzungsdaten')
topdaten = workbook.add_worksheet('Topdaten')
redner_rede_daten = workbook.add_worksheet('Redner_Rede')
beifalltext = workbook.add_worksheet('Beifalltext')
beifalldaten = workbook.add_worksheet('Beifalldaten')
wortmeldedaten = workbook.add_worksheet('Wortmeldedaten')
seldom_words_daten = workbook.add_worksheet('seldom_words')
freq_words_daten = workbook.add_worksheet('freq_words')

# Add a bold format to use to highlight cells.
bold = workbook.add_format({'bold': 1})

# Adjust the column width.
sitzungsdaten.set_column(1, 1, 15)
topdaten.set_column(1, 1, 15)
redner_rede_daten.set_column(1, 1, 15)
beifalltext.set_column(1, 1, 15)
beifalldaten.set_column(1, 1, 15)
wortmeldedaten.set_column(1, 1, 15)
seldom_words_daten.set_column(1, 1, 15)
freq_words_daten.set_column(1, 1, 15)

# Write data headers.
sitzungsdaten.write('A1', 'Sitzungsnummer', bold)
sitzungsdaten.write('B1', 'Sitzungsdatum', bold)
sitzungsdaten.write('C1', 'Wahlperiode', bold)
sitzungsdaten.write('D1', 'Anzahl_Redner', bold)
sitzungsdaten.write('E1', 'Anzahl_Redner_nach_Bereinigung', bold)
sitzungsdaten.write('F1', 'Anzahl_Tagesordnungspunkte', bold)
sitzungsdaten.write('G1', 'Anzahl_Tagesordnungspunkte_nach_Bereinigung', bold)
sitzungsdaten.write('H1', 'Anzahl_Wortmeldungen', bold)
sitzungsdaten.write('I1', 'Anzahl_Beifaelle', bold)


topdaten.write('A1', 'Sitzungsnummer', bold)
topdaten.write('B1', 'Tagesordnungspunkt', bold)
topdaten.write('C1', 'Tagesordnungspunktbezeichnung', bold)
topdaten.write('D1', 'gefundenes Synonym', bold)
topdaten.write('E1', 'Top_Einordnung_Kategorie', bold)

#redner_rede_daten.write('A1', 'Tagesordnungspunkt', bold)
redner_rede_daten.write('A1', 'Tagesordnungspunktbezeichnung', bold)
redner_rede_daten.write('B1', 'Redner', bold)
redner_rede_daten.write('C1', 'Geschlecht', bold)
redner_rede_daten.write('D1', 'Partei', bold)
redner_rede_daten.write('E1', 'clean_rede', bold)
redner_rede_daten.write('F1', 'Zeile_Beginn', bold)
redner_rede_daten.write('G1', 'Zeile_Ende', bold)
redner_rede_daten.write('H1', 'Sentiment-Wert-Rede', bold)
redner_rede_daten.write('I1', 'Sentiment-Gesamt-Rede', bold)
redner_rede_daten.write('J1', 'rede_id', bold)

beifalltext.write('A1', 'rede_id', bold)
beifalltext.write('B1', 'Beifalltext', bold)
beifalltext.write('C1', 'Zeile_Beifalltext', bold)
beifalltext.write('D1', 'Beifall_ID', bold)

beifalldaten.write('A1', 'Beifall_ID', bold)
beifalldaten.write('B1', 'Beifall_von_welcher_Partei/Abgeordneten', bold)
#beifalldaten.write('C1', 'Zeile_Beifalltext_Uebernahme', bold)
beifalldaten.write('C1', 'Zaehler', bold)

wortmeldedaten.write('A1', 'rede_id', bold)
wortmeldedaten.write('B1', 'Wortmeldungen', bold)
wortmeldedaten.write('C1', 'Wer', bold)
wortmeldedaten.write('D1', 'Partei', bold)
wortmeldedaten.write('E1', 'Text', bold)
wortmeldedaten.write('F1', 'Zeile_Wortmeldung', bold)
wortmeldedaten.write('G1', 'Sentiment-Wert', bold)
wortmeldedaten.write('H1', 'Sentiment-Gesamt', bold)


seldom_words_daten.write('A1', 'rede_id', bold)
seldom_words_daten.write('B1', 'Seldom_words', bold)
seldom_words_daten.write('C1', 'number_seldom_words_in_speech', bold)

freq_words_daten.write('A1', 'rede_id', bold)
freq_words_daten.write('B1', 'freq_words', bold)
freq_words_daten.write('C1', 'number_freq_words_in_speech', bold)


def get_content():
    '''
    ÄNDERUNG! Wir gehen alle Zeilen der TXT durch und übergeben die Zeilen in die Liste "liste_zeilen"
    Holt den Content fuer alle Seiten eines Protokolls.
    :rtype string_sitzung: String
    :return string_sitzung: Kompletter Sitzungsinhalt in einer Zeichenkette.
    '''
    global liste_zeilen
    f = codecs.open("txt_protokolle/18" + aktuelle_sitzungsnummer + "-data.txt", "r", "utf-8")
    lines = f.readlines()
    f.close()
    liste_sitzungsinhalt = []
    string_sitzung = ''
    for line in lines:
        line = line.strip()
        # liste_sitzungsinhalt.append(line)
        # #print(line)
        # string_sitzung = ' '.join(liste_sitzungsinhalt)
        if line.__contains__('ğ'):
            line = line.replace('ğ', 'g')

        # if line.__contains__('è'):
        #     line = line.replace('è', 'e')
        #
        # if line.__contains__('é'):
        #     line = line.replace('é', 'e')

            # print(list_element)
        liste_zeilen.append(line)

    return liste_zeilen


def hole_alle_redner_aus_cleaned_sortierte_sitzung(cleaned_sortierte_sitzung):
    aktuelle_sitzung = cleaned_sortierte_sitzung['Sitzung ' + aktuelle_sitzungsnummer]
    liste_alle_redner = []

    for topic in aktuelle_sitzung['TOPs']:
        for redner in topic['Redner']:
            liste_alle_redner.append(redner)
    return liste_alle_redner


def get_zeile_of_txt_from_string(string, list_sitzungs_zeilen):
    index = 0
    try:
        index = list_sitzungs_zeilen.index(string)

    except ValueError as err:
        #print(err)
        #print('Exception abgefangen in get_zeile_of_txt_from_string()')
        return index

    return index


def split_and_analyse_content(liste_zeilen, sitzungen):
    '''
    ÄNDERUNG
    Seiteninhalte des Protokolls werden zu Sätze, die wiederum zu Listenelemente werden
    entfernen von "\n" und "-" aus Listenelemente.
    :type liste_zeilen: list
    :param liste_zeilen: Kompletter Sitzungsinhalt in einer Zeichenkette.
    '''
    isActive = True
    counter = 0
    global deleted_speechers_in_analyse_content
    deleted_speechers_in_analyse_content = []
    while isActive:
        if 'Beginn:' in liste_zeilen[counter]:
            isActive = False
        else:
            global list_elements_till_first_speech
            indexierte_liste.append(liste_zeilen[counter])
            list_elements_till_first_speech.append(liste_zeilen[counter])  # Teile mit TOP, ZTOP,...
            counter += 1
    #print(list_elements_till_first_speech)
    #list = sent_tokenize(liste_zeilen)
    alle_redner_einer_sitzung = hole_alle_redner_aus_cleaned_sortierte_sitzung(sitzungen)
    list_elements = []
    for i in range(counter+1,len(liste_zeilen)):
        list_elements.append(liste_zeilen[i])
        indexierte_liste.append(liste_zeilen[i])
        list_element = liste_zeilen[i]
        analyse_content_element(list_element, i, alle_redner_einer_sitzung, sitzungen)

        #set_number(i)
        #if list_element.__contains__('(Schluss:'):
         #   global ende_der_letzten_rede
          #  ende_der_letzten_rede = i


def analyse_content_element(list_element, i, alle_redner_einer_sitzung, sitzungen):
    '''
    ÄNDERUNG
    Nimmt das listenelement auseinander und prüft, ob ein Wechsel der Redner stattfindet oder ob es sich um ein Redeteil handelt
    + Setzen Startnummer für Rede und Speicherung in Liste
    + Einsatz von StanfordParser
    :type list_element: string
    :param list_element: Übergabe aus "def content_to_dict"
    :type i: int
    :param i: Nummerierung des Listenelements
    '''

    aktuelle_sitzung = sitzungen['Sitzung ' + aktuelle_sitzungsnummer]

    temp_dict_empty_values = {'polName': '', 'partyName': ''}
    # -*- encoding: utf-8 -*-
    matchers = ['eröffne die Aussprache','Präsident', 'Präsidentin', 'Vizepräsident', 'Vizepräsidentin']

    global isMatchergefunden
    global isNameGefunden
    global redner_zaehler_fuer_iteration_durch_alle_redner

    try:
        debug_rednerzaehler = redner_zaehler_fuer_iteration_durch_alle_redner
        surname = get_surname(alle_redner_einer_sitzung[redner_zaehler_fuer_iteration_durch_alle_redner])

        if surname.__contains__('('):
            surname = remove_brackets_from_surname(surname)
    except IndexError as err:
        #print(err)
        #print('Exception abgefangen in analyse_content_element()')
        surname = 'Letzer Redner wurd durchlaufen'

    if any(m in list_element for m in matchers) and ':' in list_element and '!' not in list_element and '?' not in list_element:
        isMatchergefunden = True
        #print('setze isMatchergefunden auf True')
        if surname.__contains__('('):
            surname = remove_brackets_from_surname(surname)
        if list_element.__contains__(surname):
            redner_zaehler_fuer_iteration_durch_alle_redner += 1
            #start_Element_Rede = i-1
            surname_next_speecher = get_surname(alle_redner_einer_sitzung[redner_zaehler_fuer_iteration_durch_alle_redner])
            #if check_if_redner_in_next_5_lines(i, surname_next_speecher) == False:
                #list_with_startelement_numbers.append(start_Element_Rede)
            #list_with_startelement_numbers.append(start_Element_Rede)
            #print(list_element)
            isMatchergefunden = True
            isNameGefunden = True
            #print('setze isMatchergefunden auf True')
            if check_if_redner_in_next_5_lines(i, surname)== False:
                isMatchergefunden = False


            if check_if_redner_in_next_5_lines(i, surname_next_speecher) == True:
                isMatchergefunden = True
                isNameGefunden = False
                wichtiger_index = check_if_redner_in_next_10_lines(i, surname_next_speecher)
                if isMatchergefunden == True and wichtiger_index != 0:
                    isNameGefunden = False
                    start_Element_Rede = wichtiger_index
                    list_with_startelement_numbers.append(start_Element_Rede)
                    #print('Start-Element der Rede von' + surname + ': ' + str(start_Element_Rede))
                    #print('Listen-Element: ' + str(list_element))
                    #print('Laenge Liste Startelemente' + str(len(list_with_startelement_numbers)))
                elif isMatchergefunden == True and wichtiger_index == 0:
                    speecher_to_delete = (alle_redner_einer_sitzung[redner_zaehler_fuer_iteration_durch_alle_redner-1])
                    remove_speecher_from_list(aktuelle_sitzung, speecher_to_delete)
                    deleted_speechers_in_analyse_content.append(speecher_to_delete)

                    #alle_redner_einer_sitzung.remove(surname_to_delete)




        global isMatcherAndNameGefunden
        isMatcherAndNameGefunden = False
        #print('setze isMatcherAndNameGefunden auf False')



    elif list_element.__contains__(surname) and list_element.__contains__(':') and isMatchergefunden == True and check_if_redner_in_next_5_lines(i, surname) == True and '[' not in list_element:

        redner_zaehler_fuer_iteration_durch_alle_redner +=1
        #print('Rednerzaehler wird erhoeht!')
        isNameGefunden = True
        #print('setze isMatcherAndNameGefunden auf True')
        #print(list_element)
    elif list_element.__contains__(surname) and list_element.__contains__(':') and isMatchergefunden == False and '[' not in list_element:
        redner_zaehler_fuer_iteration_durch_alle_redner += 1
        #print('Rednerzaehler wird erhoeht!')
        isNameGefunden = True
        isMatchergefunden = True



    # elif check_if_redner_in_next_5_lines(i, surname) == True and check_if_zwischenfrage_in_next_5_lines(i) == True and isMatchergefunden == True:
    #     isMatchergefunden = False

    # if any(m in list_element for m in matchers) and ':' in list_element and '!' not in list_element and '?' not in list_element and surname in list_element:
    #     isMatchergefunden = False
    #     redner_zaehler_fuer_iteration_durch_alle_redner +=1

    if isNameGefunden == True and isMatchergefunden == True:
        isMatcherAndNameGefunden = True
        #print('setze isMatcherAndNameGefunden auf True')

    if isMatcherAndNameGefunden == True:
        isMatchergefunden = False
        isNameGefunden = False
        isMatcherAndNameGefunden = False
        #print('Startpunkt gefunden, setze alles auf False')

        start_Element_Rede = i-1
        list_with_startelement_numbers.append(start_Element_Rede)
        # print("Start_Index_Redetext: ", start_Element_Rede)
        #print('Start-Element der Rede von' + surname + ': ' + str(start_Element_Rede))
        #print('Listen-Element: ' +  str(list_element))
        #print('Laenge Liste Startelemente' + str(len(list_with_startelement_numbers)))

    #print(len(deleted_speechers_in_analyse_content))


def check_if_redner_in_next_5_lines(counter, redner_nachname):
    isFound = False
    global liste_zeilen
    i = counter
    lines_to_go = counter + 5

    while i <= lines_to_go:
        #print(len(liste_zeilen))
        if redner_nachname in liste_zeilen[i]:
            isFound = True
        i += 1

    return isFound

def check_if_redner_in_next_10_lines(counter, redner_nachname):
    isFound = False
    global liste_zeilen
    i = counter
    lines_to_go = counter + 10

    while i <= lines_to_go:
        wichtiger_index = 0
        #print('Aktuelle Zeile ',i,liste_zeilen[i])
        #print(len(liste_zeilen))
        if redner_nachname in liste_zeilen[i] and liste_zeilen[i].__contains__(':'):
            isFound = True
            wichtiger_index = counter
        i += 1

    return wichtiger_index

def check_if_zwischenfrage_in_next_5_lines(counter):
    isFound = False
    global liste_zeilen
    i= counter
    lines_to_go = counter + 5

    while i <= lines_to_go:
        if 'Zwischenfrage' in liste_zeilen[i]:
            isFound = True
        i += 1

    return isFound

def set_part_till_first_speech():
    '''
    Nimmt alle Zeilen bis zur ersten Rede auf.
    '''
    matchers = ['Beginn:']
    list_zeilen_till_first_speech = []
    global liste_zeilen
    for zeile in liste_zeilen:
        if any(m in zeile for m in matchers):
            break
        else:
            list_zeilen_till_first_speech.append(zeile)
            #print('erste Zeilen: ', zeile)


def get_all_parties():
    '''
    Gibt eine Liste zurück, welche die möglichen Parteien der Sitzungen, in Form von Strings zur Verfügung stellt.
    :type list_parties: list
    :return list_parties: Eine Liste der möglichen Parteien mit runden Klammern.
    '''
    list_parties = [
        '(DIE LINKE)',
        '(CDU/CSU)',
        '(SPD)',
        '(BÜNDNIS 90/DIE GRÜNEN)',
        '(BÜNDNIS',
        'DIE GRÜNEN)'
        '(FDP)',
        '(AFD)',
        '(DIE PIRATEN)',
        '(LINKEN)'
    ]

    return list_parties


def get_all_parties_without_brackets():
    '''
    Gibt eine Liste zurück, welche die möglichen Parteien der Sitzungen, in Form von Strings zur Verfügung stellt.
    Die Parteien werden hier ohne Klammern zur Verfügung gestellt.
    :type list_parties: list
    :return list_parties: Eine Liste der möglichen Parteien mit ohne Klammern.
    '''
    list_parties = [
        'DIE LINKE',
        'CDU/CSU',
        'SPD',
        'BÜNDNIS 90/DIE GRÜNEN',
        'BÜNDNIS',
        'DIE GRÜNEN'
        'FDP',
        'AFD)',
        'DIE PIRATEN',
        'LINKEN'
    ]

    return list_parties


def check_if_party_is_in_zeile(zeile):
    '''
    Überprüft, ob sich eine Partei in der übergebenen Zeile befindet.
    :type zeile: String
    :param zeile: Eine Zeile einer Rede.
    :rtype found_party: Boolean
    :return found_party: Ergebnis ob eine Partei in der übergebenen Zeile gefunden werden konnte.
    '''
    # Wenn das Element keinen Hinweis auf eine Partei Enthält, wird es verworfen:
    liste_parteien = get_all_parties()
    found_party = False

    for partei in liste_parteien:
        if str(partei) in zeile:
            found_party = True

    return found_party


def get_party(element):
    '''
    Holt den Parteinamen aus dem Rednernamen.
    :type element: String
    :param element: Parteiname
    :rtype: String
    :return party: Die Partei
    '''

    party = ''
    if element.__contains__(')'):
        index_of_last_open_bracket, index_of_last_closed_bracket = find_last_brackets_in_string(element)
        for letter in (element[index_of_last_open_bracket:index_of_last_closed_bracket + 1]):
            party += letter

    elif not element.__contains__(')'):
        for letter in (element[element.index('('):]):
            party += letter

    if party.__contains__('BÜNDNIS') or party.__contains__('DIE GRÜNEN'):
        party = '(BÜNDNIS 90/DIE GRÜNEN)'

    if party.__contains__('(CDU/CSU)'):
        # Wirt benötigt, falls doppelte Klamern auftreten
        party = ('(CDU/CSU)')

    return party


def get_surname(full_name):
    '''
    Holt den Nachnamen aus dem Vollständigen Namen.
    :type full_name: String
    :param full_name: Der vollständige Name eines Redners
    :rtype surname: String
    :return surname: Der Nachname
    '''
    surname = ''
    for letter in (full_name[:full_name.index(',')]):
        surname += letter

    return surname

def get_index_of_last_whitespace_in_string(string):
    '''
    Identifiziert den Index des zu letzt vorkommenden Leerzeichens in der übergebenen Zeichenkette.
    :type string: String
    :param string: Eine Zeichenkette mit Leerzeichen.
    :rtype index_of_last_whitespace: Integer
    :return index_of_last_whitespace: Index des letzten Leerzeichens.
    '''
    i = 0
    index_of_last_whitespace        = 0

    found_higher_index = True

    while found_higher_index == True:
        for letter in string[i:]:
            if letter == ' ':
                found_higher_index = True
                index_of_last_whitespace = i
            i += 1
            if i == len(string):
                found_higher_index = False

    return index_of_last_whitespace

def get_firstname(full_name):
    '''
    Holt den Vornamen aus dem Vollständigen Namen.
    :type full_name: String
    :param full_name: Der vollständige Name eines Redners.
    :rtype firstname: String
    :return firstname: Der Vorname
    '''
    index_of_last_whitespace = get_index_of_last_whitespace_in_string(full_name) + 1
    firstname = ''

    for letter in full_name[index_of_last_whitespace:]:
        firstname += letter

    return firstname

def set_number(i):
    '''
    Setzt den Index der Startreden.
    :type i: int
    :param i: Der Index
    '''
    global number_of_last_element
    number_of_last_element = i


def get_number():
    '''
    Holt den Index der Startreden.
    :rtype number_of_last_element: int
    :return number_of_last_element: Der Index
    '''
    global number_of_last_element
    return number_of_last_element

def serialize_sitzungen(dict_cleaned_sortierte_sitzungen):
    '''
    Serialisiert die Sitzungsstuktur. Da nur die letzten 10 Sitzungen auf der Webseite des Bundestages hinterlegt werden,
    speichern wir diese in Dateien.
    :type dict_cleaned_sortierte_sitzungen: dict
    :param dict_cleaned_sortierte_sitzungen: Gescrapte Sitzungsstruktur
    '''
    date = time.strftime("%d_%m_%Y")
    file = 'scraped_content/serialized_sitzungen_' + date + '.txt'
    f = open(file, 'wb')
    pickle.dump(dict_cleaned_sortierte_sitzungen, f)

def deserialize_sitzunen(path_to_serialized_file):
    '''
    Deserialisiert die gescrapt und gespeicherte Sitzunsstruktur der Bundestags-Webseite.
    :type path_to_serialized_file: string
    :param path_to_serialized_file: Pfad zur Serialisierten Datei.
    :rtype sitzungen: dict
    :return sitzungen: Die gespeicherte Sitzungsstruktur.
    '''
    file = open(path_to_serialized_file, 'rb')
    sitzungen = pickle.load(file)
    return sitzungen




def change_umlaute(string):
    '''
    Wandelt die Umlaute einer Zeichenkette um. Beispiel: ü -> ue
    :type string: String
    :param string: Der Name eines Redners ohne Umlaute.
    :rtype result_string: string
    :return result_string: Der String ohne Umlaute.
    '''
    umlaute = ['ü','ö','ä', 'ß', 'é','è', 'ğ']
    result_string = ''

    for char in string:
        if char in umlaute:

            if char == 'ü':
                char = 'u'

            if char == 'ö':
                char = 'o'

            if char == 'ä':
                char = 'a'

            if char == 'ß':
                char = 's'

            if char == 'é':
                char = 'e'

            if char == 'è':
                char = 'e'

            if char == 'ğ':
                char = 'g'

        result_string += char

    return result_string

def api_abgeordnetenwatch(politican_name):
    '''
    Anbindung an API-Abgeordnetenwatch um sich JSON abzugreifen und weitere Daten zur Person zu erhalten.
    Unterschied in der URL den Titeln der Redner betreffen dr, prof-dr ..
    :type politican_name: String
    :param politican_name: Der Name eines Politikers.
    :rtype partei: String
    :return partei: Der Parteiname des übergebenen Politikers,
    '''
    firstname = get_firstname(politican_name).lower()
    lastname = get_surname(politican_name).lower()

    firstname = change_umlaute(firstname)
    lastname = change_umlaute(lastname)
    geschlecht = 'n/a'

    if firstname.__contains__('('):
        firstname = re.sub(r'\(.*?\)', '', firstname)
    if lastname.__contains__('('):
        lastname = re.sub(r'\(.*?\)', '', lastname)

    url = 'https://www.abgeordnetenwatch.de/api/profile/' + firstname + '-' + lastname + '/profile.json'
    url2 = 'https://www.abgeordnetenwatch.de/api/profile/' + 'dr-' +firstname + '-' + lastname + '/profile.json'
    url3 = 'https://www.abgeordnetenwatch.de/api/profile/' + 'prof-dr-' +firstname + '-' + lastname + '/profile.json'


    try:
        with urllib.request.urlopen(url) as url:
            data = json.loads(url.read().decode())
            #politiker_name = data['profile']['personal']['first_name'] + " " + data['profile']['personal']['last_name']
            partei = data['profile']['party']
            geschlecht = data['profile']['personal']['gender']

    except urllib.error.HTTPError as err:
        if err.code == 404:
            #print('exception abgefangen in api_abgeordnetenwatch')
            try:

                with urllib.request.urlopen(url2) as url2:
                    data = json.loads(url2.read().decode())
                    # politiker_name = data['profile']['personal']['first_name'] + " " + data['profile']['personal']['last_name']
                    partei = data['profile']['party']
                    geschlecht = data['profile']['personal']['gender']

            except urllib.error.HTTPError as err:

                try:
                    with urllib.request.urlopen(url3) as url3:
                        data = json.loads(url3.read().decode())
                        # politiker_name = data['profile']['personal']['first_name'] + " " + data['profile']['personal']['last_name']
                        partei = data['profile']['party']
                        geschlecht = data['profile']['personal']['gender']

                except urllib.error.HTTPError as err:
                    partei = 'Api-Error-Code 404: Seite konnte nicht gefunden werden: ' + "https://www.abgeordnetenwatch.de/api/profile/" + firstname + '-' + lastname + '/profile.json'
                    geschlecht = 'Api-Error-Code 404: Seite konnte nicht gefunden werden: ' + "https://www.abgeordnetenwatch.de/api/profile/" + firstname + '-' + lastname + '/profile.json'

        else:
            #print('AW-API Fehler')
            #print(err)
            error_code = str(err)
            partei = error_code + " https://www.abgeordnetenwatch.de/api/profile/" + firstname + '-' + lastname + '/profile.json'

    return '(' + partei + ')', geschlecht


def get_start_and_end_of_a_speech():
    '''
    Bestimmung von Start und Ende der Reden.
    :rtype liste_mit_Startnummern_und_End: List
    :return liste_mit_Startnummern_und_End: Liste mit Liste mit Start-und Endnummern
    '''
    #print("Liste mit Startnummern: ", list_with_startelement_numbers)
    #print(len(list_with_startelement_numbers))
    liste_mit_Startnummern_und_End = []
    global liste_mit_Endnummern
    i = 0
    x = 1
    while i < len(list_with_startelement_numbers) - 1:
        liste_mit_Endnummern.insert(i, list_with_startelement_numbers[x] - 1)
        if i == len(list_with_startelement_numbers) - 2:
            liste_mit_Endnummern.append(get_number())
        i += 1
        x += 1
    #print('Liste mit Endnummern: ', liste_mit_Endnummern)
    #print(len(liste_mit_Endnummern))
    # Füllen mit Start und Endnummern
    i = 0
    while i <= len(list_with_startelement_numbers) - 1:
        liste_mit_Startnummern_und_End.append(list_with_startelement_numbers[i])
        liste_mit_Startnummern_und_End.append(liste_mit_Endnummern[i])
        i += 1
    #print('Liste mit Start-und Endnummern: ', liste_mit_Startnummern_und_End)
    #print(len(liste_mit_Startnummern_und_End))
    global list_with_startEnd_numbers
    list_with_startEnd_numbers = liste_mit_Startnummern_und_End
    return liste_mit_Startnummern_und_End


def get_all_speeches(liste_mit_Startnummern_und_End):
    '''
    Befüllen der Liste "alle_Reden_einer_Sitzung" mit Reden.
    :type liste_mit_Startnummern_und_End; List
    :param liste_mit_Startnummern_und_End: Liste mit der Start- und Endnummer einer Rede.
    :rtype alle_Reden_einer_Sitzung: Liste mit allen Reden einer Sitzung.
    :return alle_Reden_einer_Sitzung: Liste mit Reden
    '''
    alle_Reden_einer_Sitzung = []
    x = 0
    y = 1
    start = 1
    end = len(liste_mit_Startnummern_und_End) - 1
    active = True
    while active:
        if start > end:
            active = False
        else:
            alle_Reden_einer_Sitzung.append(indexierte_liste[
                                            liste_mit_Startnummern_und_End[x]:liste_mit_Startnummern_und_End[
                                                y]])  # [alle zwischen Start:Ende]
        x += 2
        y += 2
        start += 2

    return alle_Reden_einer_Sitzung

def speech_to_words_if_word_isalpha(string_speech):
    '''
    Die Rede wird gesäubert indem alle Wörter herausgefiltert werden, hierbei werden Satzzeichen, Zahlen (nicht alphabetisch) entfernt.
    :type string_speech: String
    :param string_speech: Eine vollständige Rede.
    :rtype liste_speech_word_tokenized: List
    :return liste_speech_word_tokenized: Einzelne Wörter der Rede.
    '''
    words = word_tokenize(str(string_speech))
    # RedeText enthealt noch  „!“, „,“, „.“ und Doppelungen und so weiter
    # saebern des RedeTextes von Zeichen !!! ABER !!! doppelte Woerter lassen, da die Haeufigkeit spaeter gezaehlt werden soll
    liste_speech_word_tokenized = [word for word in words if word.isalpha()]
    return liste_speech_word_tokenized


def count_seldom_frequently(freq_CleandedSpeech):
    '''
    Ermittlung der Vorkommenshaeufigkeit der Woerter im gesaeuberten RedeText ohne stopwords.
    :type freq_CleandedSpeech: FreqDist
    :param freq_CleandedSpeech: Wörterliste
    :rtype: Lists
    :return: Listen der am häufigsten und seltensten gebrauchten Wörter einer gesäuberten Rede.
    '''

    dc_sort = (sorted(freq_CleandedSpeech.items(), key=operator.itemgetter(1),
                      reverse=True))  # sortiertes dictionary - beginnend mit groeßter Haeufigkeit

    list_frequently_words = [str(w[0]) for w in dc_sort[:10]]
    list_anzahl_frequently_words = [str(w[1]) for w in dc_sort[:10]]

    list_seldom_words = [str(w[0]) for w in dc_sort[-10:]]
    list_anzahl_seldom_words = [str(w[1]) for w in dc_sort[-10:]]

    # Wir koennen uns auch eine kummulative Verteilungsfunktion grafisch anzeigen lassen. Dazu können wir die plot()-Methode
    # auf dem fdist1-Objekt anwenden. Dazu muss jedoch das Modul matplotlib installiert sein!
    # freq_CleandedSpeech.plot(10, cumulative=True)
    return list_seldom_words, list_anzahl_seldom_words, list_frequently_words, list_anzahl_frequently_words


def lex_div_without_stopwords(liste_speech_word_tokenized):
    '''
    Lexikalische Diversität eines Redners - Vielzahl von Ausdrucksmöglichkeiten
    Die Diversität ist ein Maß für die Sprachvielfalt. Sie ist definiert als Quotient der „verschiedenen Wörter“
    dividiert durch die „Gesamtanzahl von Wörtern“ eines Textes.
    :type liste_speech_word_tokenized: List
    :param liste_speech_word_tokenized: Die einzelnen Wörter einer Rede.
    :rtype: Lists
    :return: Listen der am häufigsten und seltensten gebrauchten Wörter einer gesäuberten Rede, ohne Stopwörter.
    '''
    # Redetext ohne stop words
    stop_words = set(stopwords.words("german"))
    word_list_extension = ['Dass', 'dass', 'Der', 'Die', 'Das', 'Dem', 'Den', 'Wir', 'wir', 'Ihr', 'ihr', 'Sie', 'sie',
                           'Ich', 'ich', 'Er', 'er', 'Es', 'es', 'Du', 'du']
    for word in word_list_extension:
        stop_words.add(word)

    clean_without_stopwords = [word for word in liste_speech_word_tokenized if
                               not word in stop_words]  # herausfiltern der stopwords
    freq_Cleanded_without_stopwords = FreqDist(
        clean_without_stopwords)  # Neuzuweisung: methode FreqDist() - Ermittlung der Vorkommenshaeufigkeit der Woerter im gesaeuberten RedeText ohne stopwords
    # freq_Cleanded_without_stopwords.tabulate()                                                                  # most high-frequency parts of speech
    complete_text_with_doubles_without_stopwords = list(freq_Cleanded_without_stopwords)
    diff_words_without_doubles = set(
        complete_text_with_doubles_without_stopwords)  # "diff_words_without_doubles" enthaelt keine doppelten Woerter mehr
    # diversity_without_stopwords = len(diff_words_without_doubles) / float(len(complete_text_with_doubles_without_stopwords))

    list_seldom_words_without_stopwords, list_anzahl_seldom_words, list_frequently_words_without_stopwords, list_anzahl_frequently_words = count_seldom_frequently(
        freq_Cleanded_without_stopwords)


    return list_seldom_words_without_stopwords, list_anzahl_seldom_words, list_frequently_words_without_stopwords, list_anzahl_frequently_words


def get_zeile_of_txt_from_string_in_range(string):
    global liste_zeilen_einer_sitzung
    global result_index
    global counter_string
    string = '(' + string + ')'

    for zeile in liste_zeilen_einer_sitzung:
        if zeile == string:
            result_index = liste_zeilen_einer_sitzung.index(zeile)
            liste_zeilen_einer_sitzung[result_index] = 'gefunden ' + str(counter_string)
            counter_string +=1
            break

    return result_index+1

def create_protocol_workbook(liste_dictionary_reden_einer_sitzung, list_sitzungs_zeilen, aktuelle_sitzung):
    '''
    Erstellt ein Excel-Sheet aus den gesammelten Informationen der Sitzung(en).
    :type liste_dictionary_reden_einer_sitzung: List
    :param liste_dictionary_reden_einer_sitzung: Die Liste enthält Dictionaries mit den Reden einer Sitzung.
    '''
    global workbook

    # writing in worksheet 'Sitzungsdaten'
    global row_sitzungsdaten
    global sitzungsdaten
    global count_deleted_tops
    global ergebniszusammenfassung
    col_sitzungsdaten= 0
    sitzungnummer                                   = liste_dictionary_reden_einer_sitzung[0]['sitzungsnummer']
    sitzungsdatum                                   = liste_dictionary_reden_einer_sitzung[0]['sitzungsdatum']
    wahlperiode                                     = liste_dictionary_reden_einer_sitzung[0]['wahlperiode']
    anzahl_redner_insgesamt                         = aktuelle_sitzung['Anzahl_Redner_insgesamt']
    anzahl_redner_nach_bereinigung                  = aktuelle_sitzung['Anzahl_Redner_nach_Bereinigung']
    anzahl_tagesordnungspunkte                      = aktuelle_sitzung['Anzahl_Tagesordnungspunkte']
    anzahl_tagesordnungspunkte_nach_bereinigung     = anzahl_tagesordnungspunkte - count_deleted_tops
    anzahl_wortmeldungen                            = count_wortmeldungen_einer_sitzung(aktuelle_sitzung)
    anzahl_beifalle                                 = count_beifaelle_einer_sitzung(aktuelle_sitzung)

    ergebniszusammenfassung[aktuelle_sitzung['Sitzungsnummer']]['anzahl_Redner_nach_Bereinigung'] = aktuelle_sitzung['Anzahl_Redner_nach_Bereinigung']
    ergebniszusammenfassung[aktuelle_sitzung['Sitzungsnummer']]['anzahl_Tagesordnungspunkte_nach_Bereinigung'] = anzahl_tagesordnungspunkte_nach_bereinigung

    sitzungsdaten.write_number(row_sitzungsdaten, col_sitzungsdaten, int(sitzungnummer))
    sitzungsdaten.write(row_sitzungsdaten, col_sitzungsdaten + 1, sitzungsdatum)
    sitzungsdaten.write_number(row_sitzungsdaten, col_sitzungsdaten + 2, int(wahlperiode))
    sitzungsdaten.write_number(row_sitzungsdaten, col_sitzungsdaten + 3, int(anzahl_redner_insgesamt))
    sitzungsdaten.write_number(row_sitzungsdaten, col_sitzungsdaten + 4, int(anzahl_redner_nach_bereinigung))
    sitzungsdaten.write_number(row_sitzungsdaten, col_sitzungsdaten + 5, int(anzahl_tagesordnungspunkte))
    sitzungsdaten.write_number(row_sitzungsdaten, col_sitzungsdaten + 6, int(anzahl_tagesordnungspunkte_nach_bereinigung))
    sitzungsdaten.write_number(row_sitzungsdaten, col_sitzungsdaten + 7, int(anzahl_wortmeldungen))
    sitzungsdaten.write_number(row_sitzungsdaten, col_sitzungsdaten + 8, int(anzahl_beifalle))
    row_sitzungsdaten += 1

    # writing in worksheet 'Topdaten'
    global row_topdaten
    global topdaten
    col_topdaten = 0
    x = 0
    anzahl_reden_in_liste_dictionary_reden_einer_sitzung = len(liste_dictionary_reden_einer_sitzung)
    bar = progressbar.ProgressBar(maxval=anzahl_reden_in_liste_dictionary_reden_einer_sitzung, widgets=[ 'Schreibe in Sheet \"Topdaten\":',progressbar.AnimatedMarker(),progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()

    for dict in liste_dictionary_reden_einer_sitzung:

        # Abgleich Vokabular.xlsx mit tagesordnungspunktbezeichnung
        workbook_vokabular = xlrd.open_workbook('Vokabular_zur_Kategorisierung.xlsx')
        worksheet_blatt1 = workbook_vokabular.sheet_by_name('Blatt1')
        col_synonyms = worksheet_blatt1.col_values(0)  # Spalte mit synonymen
        col_categorie = worksheet_blatt1.col_values(2)  # Spalte mit kategorie
        matchers = col_synonyms
        list_found_synonyms = []
        string_found_synonyms = ''
        list_found_categorie = []
        string_found_categorie = ''

        if x > 0:
            # if liste_dictionary_reden_einer_sitzung[x-1]['tagesordnungspunkt'] != dict['tagesordnungspunkt'] and liste_dictionary_reden_einer_sitzung[x-1]['tagesordnungspunktbezeichnung'] !=dict['tagesordnungspunktbezeichnung']:
            if temp_tagesordnungspunkt != liste_dictionary_reden_einer_sitzung[x][
                'tagesordnungspunkt'] and temp_tagesordnungspunkt_bezeichnung != \
                    liste_dictionary_reden_einer_sitzung[x]['tagesordnungspunktbezeichnung']:
                counter = 0
                for key in ['sitzungsnummer', 'tagesordnungspunkt', 'tagesordnungspunktbezeichnung']:
                    if key == 'sitzungsnummer':
                        topdaten.write_number(row_topdaten, col_topdaten, int(dict[key]))
                    else:
                        topdaten.write(row_topdaten, col_topdaten, dict[key])

                        while counter < 1:
                            for m in range(len(matchers)):
                                matcher_element = matchers[m]
                                if temp_tagesordnungspunkt_bezeichnung.__contains__(matcher_element):
                                    list_found_synonyms.append(matcher_element)
                                    list_found_categorie.append(col_categorie[m])
                            string_found_synonyms = ' , '.join(list_found_synonyms)
                            string_found_categorie = ' , '.join(list_found_categorie)
                            topdaten.write(row_topdaten - 1, col_topdaten + 2, string_found_synonyms)
                            topdaten.write(row_topdaten - 1, col_topdaten + 3, string_found_categorie)
                            list_found_synonyms = []
                            list_found_categorie = []
                            counter += 1
                    col_topdaten += 1
                row_topdaten += 1
                col_topdaten = 0
                temp_tagesordnungspunkt = liste_dictionary_reden_einer_sitzung[x]['tagesordnungspunkt']
                temp_tagesordnungspunkt_bezeichnung = liste_dictionary_reden_einer_sitzung[x][
                    'tagesordnungspunktbezeichnung']
        else:
            temp_tagesordnungspunkt = liste_dictionary_reden_einer_sitzung[x]['tagesordnungspunkt']
            temp_tagesordnungspunkt_bezeichnung = liste_dictionary_reden_einer_sitzung[x][
                'tagesordnungspunktbezeichnung']

            topdaten.write_number(row_topdaten, col_topdaten, int(sitzungnummer))
            topdaten.write(row_topdaten, col_topdaten + 1, temp_tagesordnungspunkt)
            topdaten.write(row_topdaten, col_topdaten + 2, temp_tagesordnungspunkt_bezeichnung)
            row_topdaten += 1

        x += 1
        bar.update(x)
    bar.finish()

    # writing in worksheet 'Redner_Rede'
    global row_redner_rede
    global redner_rede_daten
    col_redner_rede = 0
    bar = progressbar.ProgressBar(maxval=anzahl_reden_in_liste_dictionary_reden_einer_sitzung,
                                  widgets=['Schreibe in Sheet \"Redner_Rede\":',progressbar.AnimatedMarker(), progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    pbar_counter = 0
    bar.start()
    for dict in liste_dictionary_reden_einer_sitzung:
        pbar_counter +=1
        for key in ['tagesordnungspunktbezeichnung', 'redner', 'geschlecht', 'partei', 'clean_rede', 'Zeile_Rede_Beginn', 'Zeile_Rede_Ende']:
            redner_rede_daten.write(row_redner_rede, col_redner_rede, dict[key])
            col_redner_rede += 1
        pos_neg, gesamt = sentiment_analyse(dict['clean_rede'])
        redner_rede_daten.write(row_redner_rede, col_redner_rede, pos_neg)
        redner_rede_daten.write(row_redner_rede, col_redner_rede + 1, gesamt)
        redner_rede_daten.write(row_redner_rede, col_redner_rede + 2, dict['rede_id_sitzungen'])
        row_redner_rede += 1
        col_redner_rede = 0
        bar.update(pbar_counter)
    bar.finish()
    # writing in worksheet 'Beifalldaten'
    global row_beifalldaten
    global temp_row_beifalldaten
    global temp_row_beifalldaten_text
    global beifalldaten
    global aktuelle_sitzungsnummer

    col_beifalldaten = 0
    counter = 1
    bar = progressbar.ProgressBar(maxval=anzahl_reden_in_liste_dictionary_reden_einer_sitzung,
                                  widgets=['Schreibe in Sheet \"Beifalldaten\":',progressbar.AnimatedMarker(),progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    pbar_counter = 0
    bar.start()
    for dict in liste_dictionary_reden_einer_sitzung:
        pbar_counter+=1
        for key in ['beifall_id', 'beifaelle_von_partei']:
            if isinstance(dict[key], list) and dict[key] == dict['beifaelle_von_partei']:
                for item in dict[key]:
                    beifalldaten.write(row_beifalldaten, col_beifalldaten, item)
                    beifalldaten.write(row_beifalldaten, col_beifalldaten + 1,
                                       str(counter) + '_' + str(dict['sitzungsnummer']))
                    row_beifalldaten += 1
                    counter += 1
            if dict[key] == dict['beifall_id']:
                n = 1
                list_anzahl_beifall_ids = []
                for x in dict['liste_counter_beifall_id']:
                    k = 0
                    l = 0
                    while k < x:
                        beifalldaten.write(temp_row_beifalldaten, col_beifalldaten,
                                           dict['rede_id_sitzungen'] + '_' + str(n))
                        # print(temp_row_beifalldaten, col, dict['rede_id_sitzungen'] + '_' + str(n))
                        k += 1
                        temp_row_beifalldaten += 1
                    list_anzahl_beifall_ids.append(k)
                    n += 1

            col_beifalldaten += 1
        col_beifalldaten = 0
        bar.update(pbar_counter)
    bar.finish()
    # writing in worksheet 'Beifalltext'
    global row_beifalltext
    global beifall_id_row
    global temp_row_beifalltext
    global beifalltext
    global liste_zeilen_einer_sitzung
    liste_zeilen_einer_sitzung = list_sitzungs_zeilen

    #global beifalldaten
    #global temp_row_beifalldaten_text
    col_beifalltext = 0
    bar = progressbar.ProgressBar(maxval=anzahl_reden_in_liste_dictionary_reden_einer_sitzung,
                                  widgets=['Schreibe in Sheet \"Beifalltext\":',progressbar.AnimatedMarker(), progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    pbar_counter = 0
    bar.start()
    for dict in liste_dictionary_reden_einer_sitzung:
        pbar_counter+=1
        for key in ['rede_id_sitzungen', 'beifaelle', 'beifall_id']:
            if isinstance(dict[key], list) and dict[key] == dict['beifaelle']:
                for item in dict['beifaelle']:
                    beifalltext.write(row_beifalltext, col_beifalltext, item)
                    row_beifalltext += 1
            if isinstance(dict[key], list) and dict[key] == dict['beifall_id']:
                for item in dict[key]:
                    beifalltext.write(beifall_id_row, col_beifalltext + 1, dict['rede_id_sitzungen'] + '_' + str(item))
                    beifall_id_row += 1
            elif dict[key] == dict['rede_id_sitzungen']:
                k = 0
                while k < len(dict['beifaelle']):
                    index_beifalltext = get_zeile_of_txt_from_string_in_range(dict['beifaelle'][k])
                    beifalltext.write(temp_row_beifalltext, col_beifalltext + 2, index_beifalltext)

                    beifalltext.write(temp_row_beifalltext, col_beifalltext, dict[key])
                    k += 1
                    temp_row_beifalltext += 1

            col_beifalltext += 1
        col_beifalltext = 0
        bar.update(pbar_counter)
    bar.finish()
    # writing in worksheet 'Wortmeldedaten'
    global row_wortmeldedaten
    global temp_row_wortmeldedaten
    global wortmeldedaten
    col_wortmeldedaten = 0
    parteiliste = get_all_parties_without_brackets()

    bar = progressbar.ProgressBar(maxval=anzahl_reden_in_liste_dictionary_reden_einer_sitzung,
                                  widgets=['Schreibe in Sheet \"Wortmeldedaten\":',progressbar.AnimatedMarker(), progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    pbar_counter = 0
    bar.start()
    for dict in liste_dictionary_reden_einer_sitzung:
        pbar_counter+=1
        liste_wer = []
        liste_text = []
        for key in ['rede_id_sitzungen', 'wortmeldungen']:
            if isinstance(dict[key], list) and dict[key] == dict['wortmeldungen']:
                for item in dict[key]:
                    wer = ''
                    partei = ''
                    text = ''
                    if item.__contains__(':'):
                        for letter in (item[:item.index(':')]):
                            wer += letter
                        if wer.__contains__('['):
                            wer_temp_ohne_partei = remove_party_from_fullname(wer)
                        wortmeldedaten.write(row_wortmeldedaten, col_wortmeldedaten + 1, wer_temp_ohne_partei)

                        for party in parteiliste:
                            if party in wer:
                                partei = party
                                break
                        wortmeldedaten.write(row_wortmeldedaten, col_wortmeldedaten + 2, partei)

                        for letter in (item[item.index(':'):]):
                            text += letter
                        text = text.replace(':','')
                        wortmeldedaten.write(row_wortmeldedaten, col_wortmeldedaten + 3, text)
                        if item.__contains__('[') and not item.__contains__('–\\xa'):
                            wortmeldedaten.write(row_wortmeldedaten, col_wortmeldedaten + 4, get_zeile_of_txt_from_string('(' + item + ')', list_sitzungs_zeilen))
                        pos_neg, gesamt = sentiment_analyse(text)
                        wortmeldedaten.write(row_wortmeldedaten, col_wortmeldedaten + 5, pos_neg)
                        wortmeldedaten.write(row_wortmeldedaten, col_wortmeldedaten + 6, gesamt)
                    else:
                        wortmeldedaten.write(row_wortmeldedaten, col_wortmeldedaten + 1, '')
                        wortmeldedaten.write(row_wortmeldedaten, col_wortmeldedaten + 2, '')
                    wortmeldedaten.write(row_wortmeldedaten, col_wortmeldedaten, item)


                    row_wortmeldedaten += 1
            else:
                k = 0
                while k < len(dict['wortmeldungen']):
                    wortmeldedaten.write(temp_row_wortmeldedaten, col_wortmeldedaten, dict[key])
                    k += 1
                    temp_row_wortmeldedaten += 1
            col_wortmeldedaten += 1
        col_wortmeldedaten = 0
        bar.update(pbar_counter)
    bar.finish()
    # writing in worksheet 'seldom_words_daten'
    global row_seldom_words_daten
    global temp_row_seldom_words_daten
    global t_row
    global seldom_words_daten
    col_seldom_words_daten = 0
    bar = progressbar.ProgressBar(maxval=anzahl_reden_in_liste_dictionary_reden_einer_sitzung,
                                  widgets=['Schreibe in Sheet \"seldom_words_daten\":',progressbar.AnimatedMarker(), progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    pbar_counter = 0
    bar.start()
    for dict in liste_dictionary_reden_einer_sitzung:
        pbar_counter+=1
        for key in ['rede_id_sitzungen', '10_seldom_words', 'number_seldom_words']:
            if isinstance(dict[key], list) and dict[key] == dict['10_seldom_words']:
                for item in dict[key]:
                    seldom_words_daten.write(row_seldom_words_daten, col_seldom_words_daten, item)
                    row_seldom_words_daten += 1
            elif isinstance(dict[key], list) and dict[key] == dict['number_seldom_words']:
                for item in dict[key]:
                    seldom_words_daten.write_number(t_row, col_seldom_words_daten, int(item))
                    t_row += 1
            else:
                k = 0
                while k < len(dict['10_seldom_words']):
                    seldom_words_daten.write(temp_row_seldom_words_daten, col_seldom_words_daten, dict[key])
                    k += 1
                    temp_row_seldom_words_daten += 1
            col_seldom_words_daten += 1
        col_seldom_words_daten = 0
        bar.update(pbar_counter)
    bar.finish()

    # writing in worksheet 'freq_words_daten'
    global row_freq_words_daten
    global temp_row_freq_words_daten
    global t_row_freq_words_daten
    global freq_words_daten
    col_freq_words_daten = 0
    bar = progressbar.ProgressBar(maxval=anzahl_reden_in_liste_dictionary_reden_einer_sitzung,
                                  widgets=['Schreibe in Sheet \"freq_words_daten\":',progressbar.AnimatedMarker(), progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    pbar_counter = 0
    bar.start()
    for dict in liste_dictionary_reden_einer_sitzung:
        pbar_counter+=1
        for key in ['rede_id_sitzungen', '10_frequently_words', 'number_frequently_words']:
            if isinstance(dict[key], list) and dict[key] == dict['10_frequently_words']:
                for item in dict[key]:
                    freq_words_daten.write(row_freq_words_daten, col_freq_words_daten, item)
                    row_freq_words_daten += 1
            elif isinstance(dict[key], list) and dict[key] == dict['number_frequently_words']:
                for item in dict[key]:
                    freq_words_daten.write_number(t_row_freq_words_daten, col_freq_words_daten, int(item))
                    t_row_freq_words_daten += 1
            else:
                k = 0
                while k < len(dict['10_frequently_words']):
                    freq_words_daten.write(temp_row_freq_words_daten, col_freq_words_daten, dict[key])
                    k += 1
                    temp_row_freq_words_daten += 1
            col_freq_words_daten += 1
        col_freq_words_daten = 0
        bar.update(pbar_counter)
    bar.finish()

def clean_speeches(alle_Reden_einer_Sitzung):
    '''
    Holt alle Zwischenrufe, Beifälle, Unruhe, etc. aus einer Rede.
    :type alle_Reden_einer_Sitzung: List
    :param alle_Reden_einer_Sitzung: Beinhaltet die Reden einer Sitzung in Unterlisten.
    :rtype liste_dictionary_reden_einer_sitzung: List
    :return liste_dictionary_reden_einer_sitzung: Beinhaltet die Reden einer Sitzung in Dictionaries.
    '''
    # gehe jede Rede durch
    # wenn (...) kommt dann entferne diesen Teil aus Rede
    # entfernten Teil analysieren und zwischenspeichern
    regex = re.compile(".*?\((.*?)\)")
    liste_dictionary_reden_einer_sitzung = []
    rede_id = 1


    for rede in alle_Reden_einer_Sitzung:

        counter_beifaelle = 0
        counter_wortmeldungen = 0
        clean_rede = ''
        liste_beifaelle = []
        liste_wortmeldungen = []
        dict_beifaelle = {}
        dict_wortmeldungen = {}
        result_dictionary = {}
        string_rede = ''
        liste_treffer = []
        liste_beifaelle_extract_partei = []

        string_rede = ' '.join(rede)
        if string_rede.__contains__('schließe die Aussprache'):
            string_rede =string_rede.split('schließe die Aussprache')[0]
        #print(string_rede)
        liste_treffer = re.findall(regex, string_rede)
        liste_parteien = get_all_parties_without_brackets()
        liste_beifall_id = []
        beifall_id = 1
        liste_counter_beifall_id = []

        for i in liste_treffer:
            #print('Eintrag: ', i)

            party_found = False
            if i.__contains__('Beifall'):
                liste_beifall_id.append(str(beifall_id))
                counter_beifaelle += 1
                liste_beifaelle.append(i)  # Hinzufügen aller Beifälle einer Rede

                counter = 0
                for x in liste_parteien:
                    if i.__contains__(x):
                        party_found = True
                        liste_beifaelle_extract_partei.append(x)
                        counter += 1
                if party_found == False:
                    liste_counter_beifall_id.append(0)
                elif party_found == True:
                    liste_counter_beifall_id.append(counter)
                beifall_id += 1
            else:
                if i.__contains__('['):
                    counter_wortmeldungen += 1
                    liste_wortmeldungen.append(i)  # Hinzufügen aller Wortmeldungen einer Rede
                else:
                    pass

            string_rede = string_rede.replace('(' + i + ')', '')

        ### Analyse Redetext - Haufigkeit und lexikalische Diversitaet
        liste_speech_word_tokenized = speech_to_words_if_word_isalpha(string_rede)
        list_seldom_words_without_stopwords, list_number_seldom_words, list_frequently_words_without_stopwords, list_number_freq_words = lex_div_without_stopwords(
            liste_speech_word_tokenized)

        result_dictionary_einer_rede = {
            'sitzungsnummer': '',
            'sitzungsdatum': '',
            'wahlperiode': '',
            'tagesordnungspunkt': '',
            'tagesordnungspunktbezeichnung': '',
            'redner': '',
            'rede_id_sitzungen': rede_id,
            'rede_id': rede_id,
            'clean_rede': string_rede,
            'beifaelle': liste_beifaelle,
            'beifall_id': liste_beifall_id,
            'beifaelle_von_partei': liste_beifaelle_extract_partei,
            'liste_counter_beifall_id': liste_counter_beifall_id,
            'anzahl_beifaelle': counter_beifaelle,
            'wortmeldungen': liste_wortmeldungen,
            'anzahl_wortmeldungen': counter_wortmeldungen,
            '10_seldom_words': list_seldom_words_without_stopwords,
            'number_seldom_words': list_number_seldom_words,
            '10_frequently_words': list_frequently_words_without_stopwords,
            'number_frequently_words': list_number_freq_words

        }
        liste_dictionary_reden_einer_sitzung.append(result_dictionary_einer_rede)
        rede_id += 1
    return liste_dictionary_reden_einer_sitzung


def start_scraping_with_chrome(url):
    '''
    Scrapt eine Webseite mit dem Google-Chrome-Browser anhand einer übergebenen URL.
    :type url: String
    :param url: Die URL der zu scrapendenden Webseite.
    :rtype chrome: Selenium-Chrome-Webdriver-Objekt
    :return chrome: Die Chrome-Webbrowser-Session.
    '''
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')

    # Fuer Windows:
    #chrome = webdriver.Chrome('C:/Python36-32/BrowserDriver/chromedriver.exe', chrome_options=chrome_options)

    #Fuer Linux:
    chrome = webdriver.Chrome('/usr/bin/chromedriver', chrome_options=chrome_options)

    chrome.get(url)
    return chrome

def get_files_from_server_via_sitzungsnummern(list_sitzungsnummern):
    '''
    Nimmt eine Liste mit Sitzungsnummern entgegen und lädt die Plenarprotokolle anhand der Sitzungsnummern vom Server herunter
    :type list_sitzungsnummern: list
    :param list_sitzungsnummern: Liste mit Sitzungsnummern.
    '''

    chrome = start_scraping_with_chrome('http://www.bundestag.de/ajax/filterlist/de/dokumente/protokolle/plenarprotokolle/plenarprotokolle/-/455046/h_6810466be65964217012227c14bad20f?limit=10&noFilterSet=true')
    soup = BeautifulSoup(chrome.page_source, 'lxml')
    list_link_txts = []

    for item in soup.find_all(attrs={'class': 'bt-linkliste'}):
        for link in item.find_all('a'):
            list_link_txts.append('http://www.bundestag.de' + (link.get('href')))

    for url in list_link_txts:
        # Linux:
        os.system('wget -N -P txt_protokolle/'+ ' ' + url)
        # Windows:
        #output_directory = 'C:/PycharmProjects/AbgeordnetenWatch/txt_protokolle/'
        #wget.download(url, out=output_directory)

def get_new_zp_topic(topic):
    '''
    Erstellt eine neue Bezeichnungen für einen Zusatztagespunkt.
    :type topic: String
    :param topic: Zusatztagespunktbezeichnung
    :rtype new_topic: String
    :return new_topic: Neue Zusatztagespunktbezeichnung
    '''
    new_topic_letters_counter = topic.index('+')
    counter = 0
    new_topic = ''

    for letter in str(topic):
        if counter <= new_topic_letters_counter:
            counter += 1
            new_topic += letter
    return new_topic


def rebuild_topic(topic, whitespaces_to_jump):
    '''
    Nimmt den Tagesordnungspunkt auseinander und gibt den 'TOP X' zurück
    :type topic: String
    :param topic: Tagesordnungspunkt (z.B. 'TOP 40 Bundeswehreinsatz im Mittelmeer')
    :type whitespaces_to_jump: Int
    :param whitespaces_to_jump: Spaces die es zu überspringen gilt, bis der Tagesordnungspunktname erreicht wurde (meistens 2)
    :rtype new_topic: String
    :return new_topic: z.B. 'TOP 40 Bundeswehreinsatz im Mittelmeer' wird übergeben mit whitespaces_to_jump = 2 -> returned 'TOP 40'
    '''

    new_topic = ''
    if 'Sitzungseröffnung' in topic:
        new_topic = 'TOP'
    elif '+' in topic:
        new_topic = get_new_zp_topic(topic)
    else:
        if 'Legislaturbericht Digitale Agenda 2014 bis 2017' in topic:
            pass
        found_spaces = 0
        for letter in str(topic):
            if letter != ' ' and found_spaces < whitespaces_to_jump:
                new_topic = new_topic + letter

            elif letter == ' ' and found_spaces < whitespaces_to_jump:
                new_topic = new_topic + letter
                found_spaces = found_spaces + 1
    return new_topic.strip()


def get_topic_name_from_topic_number(top, topic):
    '''
    Entfernt die 'TOP X' Nummer aus dem Tagesordnungspunkt und gibt dann nur den/die eigentlichen Namen/Beschreibung zurück
    :type top: String
    :param top: z.B.: 'TOP 40'
    :type topic: String
    :param topic: z.B. 'TOP 40 Bundeswehreinsatz im Mittelmeer'
    :rtype topic_name: String
    :return topic_name: Tagesordnungspunkt-Beschreibung z.B.: 'Bundeswehreinsatz im Mittelmeer'
    '''
    topic_name = topic.replace(top, '')
    topic_name = topic_name.strip()
    return topic_name


def get_alle_tops_and_alle_sitzungen_from_soup(soup):
    '''
    Holt alle Tagesordnungspunkte und die Metadaten der vorhandenen Sitzungen aus der "Wundervollen Suppe".
    :type soup: BeautifulSoup
    :param soup: Das wundervolle Süppchen.
    :rtype dict_tops_and_sitzungen: dict
    :return dict_tops_and_sitzungen: Dictionary - Mit allen unbearbeiteten TOPs (Liste); Sitzungsmetadaten (Dictionary)
    '''
    dict = {'num_Sitzung': '', 'num_Wahlperiode': '', 'dat_Sitzung': '', 'top': {}}
    liste_dict = []
    liste_top = []
    alle_tops_list = []
    alle_sitzungsnummern_der_vorhandenen_plenarprotokolle = []

    for item in soup.find_all('strong'):
        # print(item.get_text())
        if item.get_text().__contains__('Wahlperiode'):
            dict = {'num_Sitzung': item.get_text()[7:10], 'num_Wahlperiode': item.get_text()[21:23],
                    'dat_Sitzung': item.get_text()[38:48]}
            alle_sitzungsnummern_der_vorhandenen_plenarprotokolle.append(item.get_text()[7:10])
            liste_dict.append(dict)
        if item.get_text().__contains__('TOP'):
            # print(para.get_text())
            liste_top.append(item.get_text())
        alle_tops_list.append(item.get_text())

    dict_tops_and_sitzungen = {'TOPs': alle_tops_list, 'Alle_Sitzungen': liste_dict}

    return dict_tops_and_sitzungen, alle_sitzungsnummern_der_vorhandenen_plenarprotokolle


def get_alle_sitzungen_mit_start_und_ende_der_topic(alle_tops_list, alle_sitzungen):
    '''
    Gibt alle Sitzungen zurück samt Topics, deren Rednern, sowie die Sitzungsmetadaten. (Sitzungsnummer, Datum, Wahlperiode)
    Vereint hierbei die unbearbeiteten Topics mit den Sitzungsmetadaten.
    :type alle_tops_list: List
    :param alle_tops_list: Die Tgesordnungspunkte
    :type alle_sitzungen: List
    :param alle_sitzungen: Die Sitzungsmetadaten
    :rtype alle_sitzungen: List
    :return alle_sitzungen: Die erweiterten Sitzungsdaten.
    '''
    liste_nummern_sitzungsstart = []
    liste_nummern_sitzungsende = []
    for i, j in enumerate(alle_tops_list):
        if j == '\n  TOP Sitzungseröffnung ':
            liste_nummern_sitzungsstart.append(i)
    for i, j in enumerate(alle_tops_list):
        if j == '\n  TOP Sitzungsende ':
            liste_nummern_sitzungsende.append(i)

    eine_Sitzung = []
    alle = []
    x = 0
    start = 0
    end = len(liste_nummern_sitzungsende) - 1
    active = True
    while active:
        eine_Sitzung = []
        if start > end:
            active = False
        else:
            eine_Sitzung.append(alle_tops_list[liste_nummern_sitzungsstart[x]:liste_nummern_sitzungsende[
                x]])  # [alle zwischen Start:Ende]

            alle_sitzungen[x]['top'] = eine_Sitzung
        x += 1
        start += 1
        alle.append(eine_Sitzung)

    return alle_sitzungen


def sort_dict_topics_via_topic_id(dict_topics):
    '''
    Erhält ein Dictionary und sortiert es anhand der Topic-ID in eine Liste.
    :type dict_topics: dict
    :param dict_topics: Die Tagesordnungspunkte
    :rtype list_sorted_topics: List
    :return list_sorted_topics: Nach der Topic-ID sortierten Tagesordnungspunkte.
    '''
    if len(dict_topics) > 1:
        dict_temp = {}
        list_sorted_topics = []
        for topic in sorted(dict_topics):
            topic_name = str(topic)
            topic_id = dict_topics[topic_name]['TOP_ID']
            dict_temp[topic_name] = topic_id

        for item in sorted(dict_temp.items(), key=lambda x: x[1]):
            temp_item = dict_topics[item[0]]
            temp_item['Top_Key'] = item[0]
            list_sorted_topics.append(temp_item)

        return list_sorted_topics


def sort_topics_to_sitzung(alle_sitzungen):
    '''
    Bearbeitet die Tagesordnungspunkte, sortiert die Redner den entsprechenden Tagesordnungspunkten zu. Zuordnung der
    Sitzungs-Metadaten in die entsprechende Sitzung.
    :type alle_sitzungen: list
    :param alle_sitzungen: Die Sitzungsstruktur aller Sitzungen.
    :rtype dict_sitzungen: dict
    :return dict_sitzungen: Die Sitzungsstruktur aller verfügbaren Sitzungen inklusive der Tagesordnungspunkte und den entsprechenden Rednern.
    '''
    dict_sitzungen = {}

    for sitzung in alle_sitzungen:
        tops = sitzung['top'][0]
        sitzungs_datum = sitzung['dat_Sitzung']
        wahlperiode = sitzung['num_Wahlperiode']
        sitzungs_nummer = sitzung['num_Sitzung']

        tops.index
        dict_rede = {}
        dict_sitzung = {}
        list_redner = []
        top_counter = -1

        top_zwischenspeicher = ''
        dict_topics = {}
        topic_id = 0
        topic_number_key_cache = ''
        for i in range(len(tops)):
            topic = tops[i]
            topic = topic.strip()

            # print(topic)
            if topic.__contains__('TOP'):
                top_counter = top_counter + 1
                list_redner = []
                top_number_key = rebuild_topic(topic, 2)
                topic_number_key_cache = top_number_key
                if top_number_key != 'TOP':
                    topic_id += 1
                    topic_number_key_cache = topic
                    top_name = get_topic_name_from_topic_number(top_number_key, topic)
                    if top_number_key == 'TOP ZP':
                        top_number_key += topic_number_key_cache
                        top_name = top_number_key
                    dict_topics[top_number_key] = {'Tagesordnungspunkt': top_name, 'TOP_ID': topic_id}

            else:

                list_redner.append(topic)

            if top_number_key != 'TOP':
                dict_topics[top_number_key]['Redner'] = list_redner
        list_sorted_topics = sort_dict_topics_via_topic_id(dict_topics)
        dict_sitzung = {
            'Sitzungsdatum': sitzungs_datum,
            'Wahlperiode': wahlperiode,
            'TOPs': list_sorted_topics,
            'Sitzungsnummer': sitzungs_nummer
        }

        dict_sitzungen['Sitzung ' + sitzungs_nummer] = dict_sitzung

    return dict_sitzungen


def delete_first_and_last_speecher_from_list(dict_sitzungen):
    '''
    Entfernt den ersten und den letzten Redner aus jedem Tagesordnungspunkt.
    :type dict_sitzungen: dict
    :param dict_sitzungen: Die Sitzungsstruktur aller verfügbarer Sitzungen.
    :rtype dict_sitzungen: dict
    :return dict_sitzungen: Die gesäuberte Sitzungsstruktur aller verfügbarer Sitzungen
    '''

    sitzung = 'Sitzung ' + aktuelle_sitzungsnummer
    temp_speecher_list = dict_sitzungen[sitzung]['TOPs']
    top_counter = 0
    while top_counter < len(temp_speecher_list):
        '''Problem mit der ID in lösche Eintrag in der Liste an der Stelle -1'''
        if len(temp_speecher_list[top_counter]['Redner']) >= 3:
            temp_top_liste = temp_speecher_list[top_counter]['Redner']
            temp_top_liste.remove(temp_top_liste[0])
            del temp_top_liste[-1]
            top_counter += 1

        elif len(temp_speecher_list[top_counter]['Redner']) < 3:
            del temp_speecher_list[top_counter]

    anzahl_redner_in_aktueller_sitzung = count_speecher_from_cleaned_sortierte_sitzung(dict_sitzungen[sitzung])
    anzahl_topics_in_aktueller_sitzung = len(dict_sitzungen[sitzung]['TOPs'])

    dict_sitzungen[sitzung]['Anzahl_Redner_insgesamt'] = anzahl_redner_in_aktueller_sitzung
    dict_sitzungen[sitzung]['Anzahl_Tagesordnungspunkte'] = anzahl_topics_in_aktueller_sitzung

    return dict_sitzungen


def sort_reden_eines_tops_in_tagesordnungspunkt(reden_eines_tops, top_counter, cleaned_sortierte_sitzungen,
                                                aktuelle_sitzungsbezeichnung, lenRedeliste):
    '''
    Sortiert die Reden zu deren entsprechenden Tagesordnungspunkt.
    :type reden_eines_tops: list
    :param reden_eines_tops: Die Reden eines Tagesordnungspunktes.
    :type top_counter: int
    :param top_counter: Zähler für die Zuordnung der Tagesordnungspunkte.
    :type cleaned_sortierte_sitzungen: dict
    :param cleaned_sortierte_sitzungen: Gescrapte Sitzungsstruktur
    :type aktuelle_sitzungsbezeichnung: String
    :param aktuelle_sitzungsbezeichnung: Die aktuelle Sitzungsbezeichnung
    :rtype cleaned_sortierte_sitzungen: dict
    :return cleaned_sortierte_sitzungen: Die sortierete gescrapte Sitzungsstruktur samt einsortierten Tagesordnungspunkten, Rednern und Reden.
    '''
    i = 0
    list_sorted_redner_temp = []
    isDisplayed = False
    for redner in cleaned_sortierte_sitzungen[aktuelle_sitzungsbezeichnung]['TOPs'][top_counter]['Redner']:
        if i < lenRedeliste:
            try:
                dict_temp_redner = {str(redner): reden_eines_tops[i]}
                list_sorted_redner_temp.append(dict_temp_redner)
            except IndexError as err:
                if isDisplayed == False:
                    isDisplayed = True
                    #print('Exception abgefangen in sort_reden_eines_tops_in_tagesordnungspunkt()')

        i += 1
    cleaned_sortierte_sitzungen[aktuelle_sitzungsbezeichnung]['TOPs'][top_counter]['Redner'] = list_sorted_redner_temp
    return cleaned_sortierte_sitzungen


def merge_sitzungsstruktur_mit_reden(redeliste, cleaned_sortierte_sitzung, lenRedeliste):
    '''
    Vereint die Sitzungsstruktur mit den Reden.
    :type redeliste: list
    :param redeliste: Die Reden der Sitzung.
    :type cleaned_sortierte_sitzung
    :param cleaned_sortierte_sitzung: Die gescrapte Sitzungsstruktur.
    :type lenRedeliste: int
    :param lenRedeliste: Die Anzahl der gefundenen Reden.
    :rtype final_cleaned_sortierte_sitzung: dict
    :return final_cleaned_sortierte_sitzung: Die zusammengefügte, finale, gesäuberte Sitzung.
    '''
    aktuelle_sitzungsbezeichnung = 'Sitzung ' + aktuelle_sitzungsnummer
    aktuelle_sitzung = cleaned_sortierte_sitzungen['Sitzung ' + aktuelle_sitzungsnummer]

    global count_deleted_tops

    laenge_der_redeliste = len(redeliste)
    tops = aktuelle_sitzung['TOPs']
    reden = redeliste
    j = 0
    top_counter = 0
    for top in tops:
        i = 0
        reden_eines_tagesordnungspunkts = []

        anzahl_redner_in_topic = len(tops[top_counter]['Redner'])
        print('Anzahl Redner in Tagesordnungspunkt "' + tops[top_counter]['Tagesordnungspunkt'] + '" : ' + str(
            anzahl_redner_in_topic))

        while i < anzahl_redner_in_topic:
            try:
                i += 1
                reden_eines_tagesordnungspunkts.append(reden.pop(0))

            except IndexError as err:
                pass
                #print(err)
                #print('Exception abgefangen in merge_sitzungsstruktur_mit_reden()')




        if len(reden_eines_tagesordnungspunkts) > 1:
            final_cleaned_sortierte_sitzung = sort_reden_eines_tops_in_tagesordnungspunkt(
                reden_eines_tagesordnungspunkts, j, cleaned_sortierte_sitzung, aktuelle_sitzungsbezeichnung, lenRedeliste)
            j += 1
            top_counter += 1
        else:
            aktueller_tagesordnungspunkt = \
            cleaned_sortierte_sitzungen[aktuelle_sitzungsbezeichnung]['TOPs'][top_counter]['Tagesordnungspunkt']
            print(
                'Weniger als zwei Redner in Rednerliste des Tagesordnungspunktes "' + aktueller_tagesordnungspunkt + '". Tagesordnungspunkt wird gelöscht.')
            j += 1
            top_counter += 1
            count_deleted_tops += 1

    return final_cleaned_sortierte_sitzung


def count_speecher_from_cleaned_sortierte_sitzung(sitzung):
    '''
    Zählt die Redner einer Sitzung.
    :type sitzung: dict
    :param sitzung: Eine Parlaments-Sitzung.
    :rtype result: int
    :return result: Die Anzahl der Redner einer Sitzung.
    '''
    result = 0
    for anz_redner_je_topic in sitzung['TOPs']:
        result += len(anz_redner_je_topic['Redner'])
    return result

def count_wortmeldungen_einer_sitzung(sitzung):
    '''
    Zählt die Wortmeldungen einer Sitzung.
    :return:
    '''
    result = 0
    try:
        for top in sitzung['TOPs']:
            for dict_redner in top['Redner']:
                for redner in dict_redner:
                    result += len(dict_redner[redner]['wortmeldungen'])

    except TypeError as err:
        #print(err)
        #print('Exception abgefangen in count_wortmeldungen_einer_sitzung()')
        return 0

    return result

def count_beifaelle_einer_sitzung(sitzung):
    '''
    Zählt die Beifälle einer Sitzung.
    :param sitzung: Die aktuelle
    :return:
    '''
    global temp_counter

    result = 0
    try:
        for top in sitzung['TOPs']:
            for dict_redner in top['Redner']:
                for redner in dict_redner:
                    result += dict_redner[redner]['anzahl_beifaelle']
    except TypeError as err:
        #print(err)
        #print('Exception abgefangen in count_beifaelle_einer_sitzung()')
        return result

    return result


def remove_speecher_from_list(sitzung, surname):
    for top in sitzung['TOPs']:
        for redner in top['Redner']:
            if redner.__contains__(surname):
                top['Redner'].remove(redner)

def remove_brackets_from_surname(surname):
    index = 0
    for letter in surname:
        if letter == ' ':
            rm_entry = index
            break
        index +=1
    surname = surname[:rm_entry]
    return surname

def remove_party_from_fullname(str_fullname):
    index = 0
    for letter in str_fullname:
        if letter == '[':
            rm_entry = index
            break
        index += 1
    str_fullname = str_fullname[:rm_entry-1]
    return str_fullname

def find_last_brackets_in_string(string):
    '''
    Sicht in einem String nach den letzten runden Klammern und gibt diese samt Inhalt zurück.
    :type string: Zeichenkette mit runden Klammern "()"
    :param string: string
    :rtype index_of_last_open_bracket: int
    :return index_of_last_open_bracket: Der Index der letzten geöffneten runden Klammer innerhalb einer Zeichenkette.
    :rtype index_of_last_closed_bracket: int
    :return index_of_last_closed_bracket: Der Index der letzten geschlossenen runden Klammer innerhalb einer Zeichenkette.
    '''
    i = 0
    index_of_last_open_bracket = 0
    index_of_last_closed_bracket = 0

    found_higher_index = True

    while found_higher_index == True:
        for letter in string[i:]:
            if letter == '(':
                found_higher_index = True
                index_of_last_open_bracket = i
            i += 1
            if i == len(string):
                found_higher_index = False

    found_higher_index = True

    i = 0
    while found_higher_index == True:
        for letter in string[i:]:
            if letter == ')':
                found_higher_index = True
                index_of_last_closed_bracket = i
            i += 1
            if i == len(string):
                found_higher_index = False

    return index_of_last_open_bracket, index_of_last_closed_bracket


def set_metadaten(sitzung):
    '''
    Setzt die Metadaten einer Sitzung.
    :type sitzung: dict
    :param sitzung: Eine Parlaments-Sitzung.
    '''
    sitzungsdatum = sitzung['Sitzungsdatum']
    wahlperiode = sitzung['Wahlperiode']
    sitzungsnummer = sitzung['Sitzungsnummer']

    tagesordnungspunkt_bezeichnung = ''
    top_key = ''

    for tagesordnungspunkt in sitzung['TOPs']:

        tagesordnungspunkt_bezeichnung = tagesordnungspunkt['Tagesordnungspunkt']
        top_key = tagesordnungspunkt['Top_Key']

        for redner in tagesordnungspunkt['Redner']:
            for redner_name_temp in redner:
                redner_name = redner_name_temp
                if len(redner_name) > 1:
                    redner[redner_name]['sitzungsnummer'] = sitzungsnummer
                    redner[redner_name]['sitzungsdatum'] = sitzungsdatum
                    redner[redner_name]['tagesordnungspunktbezeichnung'] = tagesordnungspunkt_bezeichnung
                    redner[redner_name]['tagesordnungspunkt'] = top_key
                    redner[redner_name]['wahlperiode'] = wahlperiode


def mach_alle_buchstaben_klein(list):
    '''
    Wandelt alle Listenelemente um -> toLower()
    :type list: list
    :param list: Liste mit Strings
    :rtype list_result: list
    :return list_result: Liste mit Strings.
    '''

    list_result = []

    for string in list:
        string = string.lower()
        list_result.append(string)

    return list_result


def sentiment_analyse(string_to_analyse):
    '''
    Prüft jedes Wort der Wortmeldungen, anhand eines Sentiment-Wortschatzes, ob Wörter als positiv, oder negativ gerwertet werden können.
    :type string_to_analyse: string
    :param string_to_analyse: Die Wortmeldungen zu einer Rede, oder die Rede selbst.
    :rtype pos_or_neg: string
    :return pos_or_neg: Gibt "positiv", oder "negativ" zurück.
    '''


    # Wörter inkl. der Gewichtung ihrer Ausdrucksstärke
    training_set = []
    data_pos = codecs.open('sentiWS_training_set/SentiWS_v1.8c_Positive.txt', 'r', 'utf-8')
    poswords = csv.reader(data_pos, delimiter='|')
    #print(poswords)
    training_set.append([(pos[0].lower(), 'positive') for pos in poswords])

    data_neg = codecs.open('sentiWS_training_set/SentiWS_v1.8c_Negative.txt', 'r', 'utf-8')
    negwords = csv.reader(data_neg, delimiter='|')
    #print(negwords)
    training_set.append([(neg[0].lower(), 'negative') for neg in negwords])


    only_words = speech_to_words_if_word_isalpha(string_to_analyse)
    only_lower_words_in_list = mach_alle_buchstaben_klein(only_words)

    pos_or_neg = ''

    list_treffer = []
    for word in only_lower_words_in_list:
        current_word = word
        # Wir gehen alle positiven wörter durch und gleichen mit dem current_word ab
        for item in training_set[0]:
            current_item = item[0]
            if current_item == current_word:
                list_treffer.append(item)
        # Wir gehen alle negativen wörter durch und gleichen mit dem current_word ab
        for item in training_set[1]:
            current_item = item[0]
            if current_item == current_word:
                list_treffer.append(item)
    #print(list_treffer)
    if len(list_treffer)>0:
        for treffer in list_treffer:
            pos_or_neg += '; ' + ','.join(treffer)
    if pos_or_neg:
        gesamt_pos_or_neg = gesamtauswertung_sentiment_wortmeldungen(pos_or_neg)
        return pos_or_neg, gesamt_pos_or_neg
    else:
        return 'kein Eintrag in Sentiment gefunden', 'nicht definierbar'

def gesamtauswertung_sentiment_wortmeldungen(pos_or_neg):
    '''
    Zählt die positiv und negativ getaggeden Wörter einer Wortmeldung, oder einer Rede und gibt ein Fazit über das
    Gesamtergebnis zurück. Mögliche Werte: positive, negative, nicht definierbar.
    :type pos_or_neg: String
    :param pos_or_neg: Der zu analyisierende String
    :rtype wortmeldung: String
    :return wortmeldung: Das Ergebnis
    '''
    tokenized = word_tokenize(pos_or_neg)
    conter = collections.Counter(tokenized)
    number_pos = conter['positive']
    number_neg = conter['negative']
    if number_pos > number_neg:
        result = 'positive'
    elif number_pos == number_neg:
        result = 'nicht definierbar'
    else:
        result = 'negative'

    return result
def get_sitzungs_dataset_for_excel(sitzung):
    '''
    Befüllung der einzelnen Dictionaries mit den extrahierten Daten. Extrahiert die benötigten Informationen aus einer
    Sitzung für die Erstellung des Excelsheets. Hierbei erfolgt eine Überprüfung, ob die Reden zum entsprechenden Redner passen.
    Dies geschieht für jede Rede, als auch für jeden Redner, separiert pro Tagesordnungspunkt.
    :type sitzung: dict
    :param sitzung: Eine Parlaments-Sitzung
    :rtype list_result: list
    :return list_result: Die Liste mit den Informatinen der Sitzung für das Excelsheet.
    '''
    list_result = []

    global list_with_startelement_numbers
    global liste_mit_Endnummern
    global zeitstrahl_counter
    global ergebniszusammenfassung


    anzahl_redner = count_speecher_from_cleaned_sortierte_sitzung(sitzung)
    debug_ergebniszusammenfassung = ergebniszusammenfassung
    ergebniszusammenfassung[sitzung['Sitzungsnummer']] = {}
    #['Anzahl_Redner_insgesamt']] = sitzung['Anzahl_Redner_insgesamt']

    ergebniszusammenfassung[sitzung['Sitzungsnummer']]['anzahl_Redner_insgesamt'] = anzahl_redner
    ergebniszusammenfassung[sitzung['Sitzungsnummer']]['anzahl_Redner_nach_Bereinigung'] = sitzung['Anzahl_Redner_nach_Bereinigung']
    ergebniszusammenfassung[sitzung['Sitzungsnummer']]['anzahl_Tagesordnungspunkte'] = sitzung['Anzahl_Tagesordnungspunkte']
    ergebniszusammenfassung[sitzung['Sitzungsnummer']]['Wohlperiode'] = sitzung['Wahlperiode']
    ergebniszusammenfassung[sitzung['Sitzungsnummer']]['Sitzungsdatum'] = sitzung['Sitzungsdatum']

    print('\n')
    bar = progressbar.ProgressBar(maxval=anzahl_redner, widgets=['Vereinige Sitzungsstruktur mit Reden:',progressbar.AnimatedMarker(), progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()
    for tagesordnungspunkt in sitzung['TOPs']:

        for rede in tagesordnungspunkt['Redner']:
            dictionary_result = {}
            for redner in rede:
                isSpeecherinSpeech = False
                # surname = get_surname(redner)
                party = ''
                geschlecht = ''
                # Parteienvergleich
                for zeile in liste_zeilen:
                    if(len(redner)>1):
                        aktuelle_redner = get_surname(redner)
                        if aktuelle_redner.__contains__('('):
                            aktuelle_redner = remove_brackets_from_surname(aktuelle_redner)
                        if rede[redner]['clean_rede'].__contains__(aktuelle_redner):
                            isSpeecherinSpeech = True
                        if zeile.__contains__(aktuelle_redner):
                            if check_if_party_is_in_zeile(zeile) == True:
                                party = get_party(zeile)
                                break
                if isSpeecherinSpeech == True:
                    if party == '':
                        party, geschlecht = api_abgeordnetenwatch(redner)
                    if geschlecht == '':
                        party, geschlecht = api_abgeordnetenwatch(redner)

                    dictionary_result['10_frequently_words'] = rede[redner]['10_frequently_words']
                    dictionary_result['number_frequently_words'] = rede[redner]['number_frequently_words']
                    dictionary_result['10_seldom_words'] = rede[redner]['10_seldom_words']
                    dictionary_result['number_seldom_words'] = rede[redner]['number_seldom_words']
                    dictionary_result['anzahl_beifaelle'] = rede[redner]['anzahl_beifaelle']
                    dictionary_result['anzahl_wortmeldungen'] = rede[redner]['anzahl_wortmeldungen']
                    dictionary_result['beifaelle'] = rede[redner]['beifaelle']
                    dictionary_result['beifall_id'] = rede[redner]['beifall_id']
                    dictionary_result['beifaelle_von_partei'] = rede[redner]['beifaelle_von_partei']
                    dictionary_result['liste_counter_beifall_id'] = rede[redner]['liste_counter_beifall_id']
                    dictionary_result['clean_rede'] = rede[redner]['clean_rede']
                    dictionary_result['rede_id'] = str(rede[redner]['sitzungsnummer']) + '_' + str(
                        rede[redner]['rede_id'])
                    dictionary_result['rede_id_sitzungen'] = str(rede[redner]['sitzungsnummer']) + '_' + str(
                        rede[redner]['rede_id'])
                    dictionary_result['redner'] = redner
                    dictionary_result['geschlecht'] = geschlecht
                    dictionary_result['sitzungsdatum'] = rede[redner]['sitzungsdatum']
                    dictionary_result['sitzungsnummer'] = rede[redner]['sitzungsnummer']
                    dictionary_result['tagesordnungspunkt'] = rede[redner]['tagesordnungspunkt']
                    dictionary_result['tagesordnungspunktbezeichnung'] = rede[redner]['tagesordnungspunktbezeichnung']
                    dictionary_result['wahlperiode'] = rede[redner]['wahlperiode']
                    dictionary_result['wortmeldungen'] = rede[redner]['wortmeldungen']
                    dictionary_result['partei'] = party
                    # debug_zeitstrahl_counter = zeitstrahl_counter
                    # print('Zeitstrahlcounter', zeitstrahl_counter)
                    # debug_liste_mit_startnummern = list_with_startelement_numbers
                    # debug_liste_mit_endnummern = liste_mit_Endnummern
                    dictionary_result['Zeile_Rede_Beginn']  = list_with_startelement_numbers[zeitstrahl_counter]
                    dictionary_result['Zeile_Rede_Ende'] = liste_mit_Endnummern[zeitstrahl_counter]
                    # dictionary_result['Zeile_Wortmeldung']  =
                    # dictionary_result['Zeile_Beifalltext']  =
                    # dictionary_result['Zeile_Beifalltext_Uebernahme'] =

                    list_result.append(dictionary_result)
                    zeitstrahl_counter += 1
                    bar.update(zeitstrahl_counter)
    bar.finish()
    return list_result

# Hole HTML Struktur START
chrome = start_scraping_with_chrome('http://www.bundestag.de/ajax/filterlist/de/dokumente/protokolle/-/442112/h_6810466be65964217012227c14bad20f?limit=1')
print('Starte Scraping-Vorgang...')

soup = BeautifulSoup(chrome.page_source, 'lxml')
alle_tops_und_alle_sitzungen, alle_sitzungsnummern_der_vorhandenen_plenarprotokolle = get_alle_tops_and_alle_sitzungen_from_soup(soup)

get_files_from_server_via_sitzungsnummern(alle_sitzungsnummern_der_vorhandenen_plenarprotokolle)

session_counter = 0

def print_ergebniszusammenfassung():

    global ergebniszusammenfassung
    #json_ergebniszusammenfassung = json.dumps(ergebniszusammenfassung, ensure_ascii=False)

    print('\n\n[ - Zusammenfassung - ]')
    for sitzung in ergebniszusammenfassung:
        print('\n| Sitzung: ' + str(sitzung))
        print('| Anzahl Redner insgesamt: ' + str(ergebniszusammenfassung[sitzung]['anzahl_Redner_insgesamt']))
        print('| Erfolgreich zugeordnete Reden: ' + str(ergebniszusammenfassung[sitzung]['anzahl_Redner_nach_Bereinigung']))
        print('| Anzahl Tagesordnungspunkte insgesamt: ' + str(ergebniszusammenfassung[sitzung]['anzahl_Tagesordnungspunkte']))
        print('| nach Bereinigung: ' + str(ergebniszusammenfassung[sitzung]['anzahl_Tagesordnungspunkte_nach_Bereinigung']))
        erfolgsquote = float(ergebniszusammenfassung[sitzung]['anzahl_Redner_nach_Bereinigung']) /float(ergebniszusammenfassung[sitzung]['anzahl_Redner_insgesamt'])
        ergebniszusammenfassung[sitzung]['erfolgsquote'] = erfolgsquote
        print('| erreichte Erfolgsquote Sitzung ' + str(sitzung) + ': ' + str(round(erfolgsquote,2)*100), '%')

    avg_erfolgsquote = 0
    for sitzung in ergebniszusammenfassung:
        avg_erfolgsquote += ergebniszusammenfassung[sitzung]['erfolgsquote']
    avg_erfolgsquote = avg_erfolgsquote / len(ergebniszusammenfassung)

    print('\n\n| Durchschnittliche Erfolgsquote aller Sitzungen:', round(avg_erfolgsquote,2)*100, '%')


def set_globals_null():
    global indexierte_liste, start_Element_Rede, list_with_startelement_numbers, list_with_startEnd_numbers, number_of_last_element, list_elements_till_first_speech, politican_name, party_name, liste_zeilen, isMatcherAndNameGefunden, isMatchergefunden, isNameGefunden, redner_zaehler_fuer_iteration_durch_alle_redner, aktuelle_sitzungsnummer
    indexierte_liste = []  # Vorhalten von Redeteilen
    start_Element_Rede = 0
    list_with_startelement_numbers = []  # enthält Start item aller Redetexte
    list_with_startEnd_numbers = []  # enthält Start und Ende item aller Redetexte
    number_of_last_element = 0
    list_elements_till_first_speech = []  # enthält listenelemente bis zur ersten Rede
    politican_name = ""
    party_name = ""
    liste_zeilen = []
    isMatcherAndNameGefunden = False
    isMatchergefunden = False
    isNameGefunden = False
    redner_zaehler_fuer_iteration_durch_alle_redner = 0
    aktuelle_sitzungsnummer = ''


#while session_counter < 1:
while session_counter < len(alle_sitzungsnummern_der_vorhandenen_plenarprotokolle):
    zeitstrahl_counter_beginn = 0
    zeitstrahl_counter_ende = 1
    zeitstrahl_counter = 0
    aktuelle_sitzungsnummer = alle_sitzungsnummern_der_vorhandenen_plenarprotokolle[session_counter]
    session_counter += 1
    #print('Sitzungsstruktur vorhalten')

    alle_tops_list = alle_tops_und_alle_sitzungen['TOPs']
    alle_sitzungen = alle_tops_und_alle_sitzungen['Alle_Sitzungen']
    alle_sitzungen_mit_start_und_ende_der_topic = get_alle_sitzungen_mit_start_und_ende_der_topic(alle_tops_list,
                                                                                                  alle_sitzungen)
    sortierte_sitzungen = sort_topics_to_sitzung(alle_sitzungen_mit_start_und_ende_der_topic)
    cleaned_sortierte_sitzungen = delete_first_and_last_speecher_from_list(sortierte_sitzungen)

    #print('Serialisiere gescrapte Sitzungsstruktur - derzeit deaktiv')
    serialize_sitzungen(cleaned_sortierte_sitzungen)
    #deserialisierte_cleaned_sortierte_sitzungen = deserialize_sitzunen('scraped_content/serialized_sitzungen_04_07_2017.txt')
    #print('Serialisierung/Deserialisierung beendet.')
    # Hole HTML Struktur ENDE

    content = get_content()
    print('\nAnalysiere Sitzung ' + str(aktuelle_sitzungsnummer))
    names_of_entities = split_and_analyse_content(content, cleaned_sortierte_sitzungen)
    start_end_nummern_liste = get_start_and_end_of_a_speech()
    liste_alle_reden = get_all_speeches(start_end_nummern_liste)

    redeliste = clean_speeches(liste_alle_reden)

    aktuelle_sitzung = cleaned_sortierte_sitzungen['Sitzung ' + aktuelle_sitzungsnummer]
    anzahl_redner = count_speecher_from_cleaned_sortierte_sitzung(aktuelle_sitzung)

    print('\nErgebniszusammenfassung ', 'Sitzung', aktuelle_sitzungsnummer)

    print('Anzahl Redner: ' + str(anzahl_redner))
    print("Anzahl vorhandene Reden in Redeliste: " + str(len(redeliste)))
    aktuelle_sitzung['Anzahl_Redner_nach_Bereinigung'] = str(len(redeliste)-1)

    set_part_till_first_speech()
    merged_sitzung = merge_sitzungsstruktur_mit_reden(redeliste, cleaned_sortierte_sitzungen, len(redeliste))
    set_metadaten(merged_sitzung['Sitzung ' + aktuelle_sitzungsnummer])

    dataset_for_excel = get_sitzungs_dataset_for_excel(merged_sitzung['Sitzung ' + aktuelle_sitzungsnummer])
    set_globals_null()
    create_protocol_workbook(dataset_for_excel, content, aktuelle_sitzung)

print_ergebniszusammenfassung()

workbook.close()