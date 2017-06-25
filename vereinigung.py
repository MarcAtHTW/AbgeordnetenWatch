import PyPDF2
import nltk
from nltk import FreqDist
from nltk.corpus import stopwords
import operator
from nltk import sent_tokenize, word_tokenize
from nltk import StanfordPOSTagger
import os
from selenium import webdriver
from bs4 import BeautifulSoup
from operator import itemgetter
import xlsxwriter
import re
import codecs

### Start Testing_Steve ###
os.environ['JAVAHOME'] = "C:/Program Files/Java/jdk1.8.0_20/bin/java.exe"

'''
    Data extracting from Plenarprotokoll
'''
''' Globals '''
indexierte_liste = []  # Vorhalten von Redeteilen
start_Element_Rede = 0
list_with_startelement_numbers = []  # enthält Start item aller Redetexte
list_with_startEnd_numbers = []  # enthält Start und Ende item aller Redetexte
number_of_last_element = 0
list_elements_till_first_speech = []  # enthält listenelemente bis zur ersten Rede
politican_name = ""
party_name = ""


def get_content():
    '''
    Holt den Content fuer alle Seiten eines Protokolls

    :return: page_content
    '''
    # pdf_file = open('Plenarprotokoll_18_239.pdf', 'rb')
    # read_pdf = PyPDF2.PdfFileReader(pdf_file)
    # page_content = ''
    # for i in range(read_pdf.getNumPages()):
    #     print(i)
    #     pages = read_pdf.getPage(i)
    #     page_content += pages.extractText()
    #     #str(page_content.encode('UTF-8'))
    f = codecs.open("18240-data.txt", "r", "utf-8")
    lines = f.readlines()
    f.close()
    liste_sitzungsinhalt = []
    string_sitzung = ''
    for line in lines:
        line = line.strip()
        liste_sitzungsinhalt.append(line)
        print(line)
        string_sitzung = ' '.join(liste_sitzungsinhalt)
    return string_sitzung


def split_and_analyse_content(string_sitzung):
    '''
    Seiteninhalte des Protokolls werden zu Sätze, die wiederum zu Listenelemente werden
    entfernen von "\n" und "-" aus Listenelemente

    :param page_content:
    :return:
    '''
    list = sent_tokenize(string_sitzung)
    print(list)
    for i in range(len(list)):
        list_element = list[i]
        # list_element = list_element.replace("\n", "")
        # list_element = list_element.replace("-", "")
        indexierte_liste.append(list_element)  # liste ohne -, \n
        # print("item at index", i, ":", list_element)       # alle Listenelemente
        analyse_content_element(list_element, i)

        set_number(i)
        if list_element.__contains__('(Schluss:'):
            global ende_der_letzten_rede
            ende_der_letzten_rede = i
            # elif list_element.__contains__('Beginn:'):
            #     global start_der_ersten_rede
            #     start_der_ersten_rede = i

def set_number(i):
    '''
    Setzt number of listelement

    :param i:
    '''
    global number_of_last_element
    number_of_last_element = i

def get_number():
    '''
    Gibt number of listelement
    :return:
    '''
    global number_of_last_element
    return number_of_last_element

def analyse_content_element(list_element, i):
    '''
    Nimmt das listenelement auseinander und prüft, ob ein Wechsel der Redner stattfindet oder ob es sich um ein Redeteil handelt
    + Setzen Startnummer für Rede und Speicherung in Liste
    + Einsatz von StanfordParser
    :param list_element: Übergabe aus "def content_to_dict"
    :param i: Nummerierung des Listenelements
    :return:
    '''
    temp_dict_empty_values = {'polName': '', 'partyName': ''}
    # -*- encoding: utf-8 -*-
    matchers = ['erteile das Wort', 'Das Wort hat', 'das Wort.', 'erteile zu Beginn das Wort', 'hat nun das Wort',
                'Redner das Wort', 'Rednerin das Wort', 'übergebe das Wort', 'Das Wort erhält ',
                'hat jetzt das Wort für', 'Das Wort für die Bundesregierung hat',
                'Nächste Rednerin:', 'Nächster Redner', 'Nächste Rednerin für', 'Nächster Redner für',
                'Als Nächste hat das Wort', 'Als Nächster hat das Wort', 'Als Nächstes spricht', 'Als Nächste spricht',
                'Wir befinden uns noch in der Debatte und werden', 'hat jetzt um das Wort für eine',
                'Frau Kollegin Schwarzer, möchten Sie darauf antworten?', 'hat um das Wort',
                'Herr Kollege Sensburg, möchten Sie darauf antworten?', 'Erster Redner ist',
                'Ich möchte Ihnen kurz das von den Schriftführerinnen und Schriftführern ermittelte Ergebnis',
                'Jetzt hat das Wort', 'gebe das Wort', 'nächste Redner', 'nächster Redner', 'nächste Rednerin',
                'spricht jetzt', 'Nächste Rednerin ist','Nächster Redner ist', 'Nächster Redner in', 'Letzter Redner',
                'Letzte Rednerin','letzte Rednerin', 'nächste Wortmeldung',
                'spricht als Nächster', 'spricht als Nächste',
                'zunächst das Wort', 'zu Beginn das Wort', 'Wort dem',
                'Nächste Rednerin ist die Kollegin', 'Nächster Redner ist der Kollege', '(Heiterkeit)für die SPD',
                'Die erste Fragestellerin', 'Der erste Fragesteller', 'Die nächste Fragestellerin',
                'Der nächste Fragensteller', 'die nächste Fragestellerin', 'der nächste Fragensteller']
    #[x.encode('utf-8') for x in matchers]
    if any(m in list_element for m in matchers):
        print("\nWechsel Redner", i, ":", list_element)    # Listenelemente, die matchers enthalten
        if list_element.__contains__('Außerdem haben Sie nachher das Wort.') or list_element.__contains__('Jetzt hat der Kollege Herzog das Wort.'):
            pass
        else:
            start_Element_Rede = i + 1
            list_with_startelement_numbers.append(start_Element_Rede)
            print("Start_Index_Redetext: ", start_Element_Rede)
            # ''' - POS -> PartOfSpeech Verben, Nomen, ... in Listenelement mit matchers'''
            # words = word_tokenize(list_element)
            # '''extracting Named Entities - Person, Organization,...'''
            # jar = 'jars\stanford-postagger.jar'
            # model = 'jars\german-hgc.tagger'
            # pos_tagger = StanfordPOSTagger(model, jar, encoding='utf8')
            # tagged = pos_tagger.tag(words)
            # print(tagged)
            # chunkGram = r"""Eigenname: {<NE>?}"""
            # chunkParser = nltk.RegexpParser(chunkGram)
            # namedEnt = chunkParser.parse(tagged)
            # print("chunkParser: ",namedEnt)
            # #namedEnt.draw()
            # ''' extract entity names - anhand von label - NE => Eigenname'''
            # entityPers_names_subtree = []
            # for subtree in namedEnt.subtrees(filter=lambda t: t.label() == 'Eigenname'):
            #     print(subtree)
            #     entityPers_names_subtree.append(subtree[0])
            # print('entityPers_names_subtree: ',entityPers_names_subtree)
            # entityPers_names \
            #     = []
            # name = ''
            # for ne in entityPers_names_subtree:
            #     name += ' ' + ne[0]
            # entityPers_names.append(name)
            # print("Person: ",entityPers_names)
            # print("Person:",str(name))

        # Listenelement ist entweder 'Anfang bis zur ersten Rede' oder 'Redeteil'
    else:
        Rede = []
        if len(list_with_startelement_numbers) != 0:        # wenn bereits eine Startnummer (erste Rede) vorhanden
            print("Redeteil:", i, list_element)
        else:
            global list_elements_till_first_speech
            list_elements_till_first_speech.append(list_element)  # Teile mit TOP, ZTOP,...
            print('global-> erste Zeilen: ', list_element)

def api_abgeordnetenwatch(politican_name):
    '''
    Anbindung an API-Abgeordnetenwatch um sich JSON abzugreifen und weitere Daten zur Person abzugreifen
    :param politican_name
    :return: Name, Partei usw.
    '''
    import urllib.request, json
    politican_name = politican_name.lower()
    politican_name = politican_name.replace(' ', '-')
    with urllib.request.urlopen(
                            "https://www.abgeordnetenwatch.de/api/profile/" + politican_name + "/profile.json") as url:
        data = json.loads(url.read().decode())
        politiker_name = data['profile']['personal']['first_name'] + " " + data['profile']['personal']['last_name']
        partei = data['profile']['party']
    return politican_name, partei

def get_start_and_end_of_a_speech():
    '''
    Bestimmung von Start und Ende der Reden
    :return: Liste mit Liste mit Start-und Endnummern
    '''
    print("Liste mit Startnummern: ", list_with_startelement_numbers)
    print(len(list_with_startelement_numbers))
    liste_mit_Startnummern_und_End = []
    liste_mit_Endnummern = []
    i = 0
    x = 1
    while i < len(list_with_startelement_numbers) - 1:
        liste_mit_Endnummern.insert(i, list_with_startelement_numbers[x] - 1)
        if i == len(list_with_startelement_numbers) - 2:
            liste_mit_Endnummern.append(get_number())
        i += 1
        x += 1
    print('Liste mit Endnummern: ', liste_mit_Endnummern)
    print(len(liste_mit_Endnummern))
    # Füllen mit Start und Endnummern
    i = 0
    while i <= len(list_with_startelement_numbers) - 1:
        liste_mit_Startnummern_und_End.append(list_with_startelement_numbers[i])
        liste_mit_Startnummern_und_End.append(liste_mit_Endnummern[i])
        i += 1
    print('Liste mit Start-und Endnummern: ', liste_mit_Startnummern_und_End)
    print(len(liste_mit_Startnummern_und_End))
    return liste_mit_Startnummern_und_End

def get_all_speeches(liste_mit_Startnummern_und_End):
    '''
    Befüllen der Liste "alle_Reden_einer_Sitzung" mit Reden
    :return: Liste mit Reden
    '''
    alle_Reden_einer_Sitzung = []
    x = 0
    y = 1
    start = 1
    end = len(liste_mit_Startnummern_und_End) - 1
    active = True
    while active:
        print("x: ", x)
        print("y: ", y)
        print("start: ", start)
        if start > end:
            active = False
            print("false")
        else:
            alle_Reden_einer_Sitzung.append(indexierte_liste[
                                            liste_mit_Startnummern_und_End[x]:liste_mit_Startnummern_und_End[
                                                y]])  # [alle zwischen Start:Ende]
        x += 2
        y += 2
        start += 2
    print(len(alle_Reden_einer_Sitzung))
    # Ausgabe aller Reden
    # for rede in alle_Reden_einer_Sitzung:
    # print(rede)
    return alle_Reden_einer_Sitzung

    '''
    def clean_speeches(alle_Reden_einer_Sitzung):
        
        Holt alle Zwischenrufe, Beifälle, Unruhe, etc. aus einer Rede
        :return: liste_dictionary_reden_einer_sitzung
        
        import re
        # gehe jede Rede durch
        # wenn (...) kommt dann entferne diesen Teil aus Rede
        # entfernten Teil analysieren und zwischenspeichern
        regex = re.compile(".*?\((.*?)\)")
        liste_dictionary_reden_einer_sitzung = []
    
        for rede in alle_Reden_einer_Sitzung:
    
            index = 0
            clean_rede = ''
            liste_beifaelle = []
            liste_widersprueche = []
            liste_unruhe = []
            liste_wortmeldungen = []
            dict_beifaelle = {}
            dict_widersprueche = {}
            dict_unruhe = {}
            dict_wortmeldungen = {}
            result_dictionary = {}
            temp_liste_treffer = []
            eine_rede_als_kompletten_string = ''
    
            eine_rede_als_kompletten_string = ' '.join(rede)
            print('XXXX string_Rede: ', eine_rede_als_kompletten_string)
    
            index += 1
            # suche indices von Störungen
            for match in re.finditer(regex, eine_rede_als_kompletten_string):
                print('indices_Rede_unterbrechungen_alle: ', match.span())
            liste_treffer = []
            liste_treffer = re.findall(regex, eine_rede_als_kompletten_string)
            temp_liste_treffer.append(liste_treffer)
    
            for i in liste_treffer:
                if i.__contains__('Beifall'):
                    dict_beifaelle['beifalltext'] = i
                    dict_beifaelle['start_index_beifall'] = ''
                    dict_beifaelle['ende_index_beifall'] = ''
                    dict_beifaelle['redeteil_zuvor'] = ''
                    dict_beifaelle['reaktion_danach'] = ''
                    liste_beifaelle.append(dict_beifaelle)  # Hinzufügen aller Beifälle einer Rede
    
                elif i.__contains__('Widerspruch'):
                    dict_widersprueche['widerspruchtext'] = i
                    dict_widersprueche['start_index_widerspruch'] = ''
                    dict_widersprueche['ende_index_widerspruch'] = ''
                    dict_widersprueche['redeteil_zuvor'] = ''
                    dict_widersprueche['reaktion_danach'] = ''
                    liste_widersprueche.append(dict_widersprueche)  # Hinzufügen aller Widersprüche einer Rede
    
                elif i.__contains__('Unruhe'):  # Hinzufügen aller Unruhen einer Rede
                    dict_unruhe['unruhetext'] = i
                    dict_unruhe['start_index_unruhe'] = ''
                    dict_unruhe['ende_index_unruhe'] = ''
                    dict_unruhe['redeteil_zuvor'] = ''
                    dict_unruhe['reaktion_danach'] = ''
                    liste_unruhe.append(dict_unruhe)
    
                else:
                    dict_wortmeldungen['wortmeldungtext'] = i
                    dict_wortmeldungen['start_index_wortmeldung'] = ''
                    dict_wortmeldungen['ende_index_wortmeldung'] = ''
                    dict_wortmeldungen['redeteil_zuvor'] = ''
                    dict_wortmeldungen['raktion_danach'] = ''
                    liste_wortmeldungen.append(dict_wortmeldungen)  # Hinzufügen aller Wortmeldungen einer Rede
    
                    eine_rede_als_kompletten_string.replace('(' + i + ')', '')  # Entfernen von (...)
                    # clean_item = clean_item.replace('('+i+'!', '')
            clean_rede = eine_rede_als_kompletten_string
    
            result_dictionary = {
                'rede': clean_rede,
                'beifälle': liste_beifaelle,
                'widerspruch': liste_widersprueche,
                'unruhe': liste_unruhe,
                'wortmeldungen': liste_wortmeldungen
            }
            if result_dictionary['rede'] != '':
                liste_dictionary_reden_einer_sitzung.append(result_dictionary)
                # print(clean_rede)
                print('3: ', liste_beifaelle)
                print('4: ', liste_widersprueche)
                print('5: ', liste_wortmeldungen)
                print('6: ', clean_rede)
        return liste_dictionary_reden_einer_sitzung
'''

def speech_to_words_if_word_isalpha(string_speech):
    words = word_tokenize(str(string_speech))
    # RedeText enthealt noch  „!“, „,“, „.“ und Doppelungen und so weiter
    print("Anzahl aller Woerter und Zeichen: " + str(len(words)))
    # saebern des RedeTextes von Zeichen !!! ABER !!! doppelte Woerter lassen, da die Haeufigkeit spaeter gezaehlt werden soll
    liste_speech_word_tokenized = [word for word in words if word.isalpha()]
    print("Anzahl aller Woerter - AUCH DOPPELTE ohne Zeichen: " + str(len(liste_speech_word_tokenized)))
    return liste_speech_word_tokenized

def count_seldom_frequently(freq_CleandedSpeech):
    # 10 haeufigsten und seltensten Woerter einer gesaeuberten Rede
    dc_sort = (sorted(freq_CleandedSpeech.items(), key= operator.itemgetter(1), reverse = True))   # sortiertes dictionary - beginnend mit groeßter Haeufigkeit
    print(dc_sort[:10])                         # 10 haeufigsten Woerter (Wort: Anzahl)
    print([str(w[0]) for w in dc_sort[:10]])    # 10 haeufigsten Woerter (nur Wort)
    list_frequently_words = [str(w[0]) for w in dc_sort[:10]]
    print(dc_sort[-10:])                        # 10 seltensten Woerter (Wort: Anzahl)
    print([str(w[0]) for w in dc_sort[-10:]])   # 10 seltensten Woerter (nur Wort)
    list_seldom_words = [str(w[0]) for w in dc_sort[-10:]]

    # Wir koennen uns auch eine kummulative Verteilungsfunktion grafisch anzeigen lassen. Dazu können wir die plot()-Methode
    # auf dem fdist1-Objekt anwenden. Dazu muss jedoch das Modul matplotlib installiert sein!
    #freq_CleandedSpeech.plot(10, cumulative=True)
    return list_seldom_words, list_frequently_words

def lex_div_without_stopwords(liste_speech_word_tokenized):
    ###### Lexikalische Diversität eines Redners - Vielzahl von Ausdrucksmöglichkeiten #######
    # Die Diversität ist ein Maß für die Sprachvielfalt. Sie ist definiert als Quotient der „verschiedenen Wörter“ dividiert durch die „Gesamtanzahl von Wörtern“ eines Textes.

    # Redetext ohne stop words
    stop_words = set(stopwords.words("german"))
    #print("\n" + "STOPWORDS: " + "\n" + str(stop_words) + "\n")
    word_list_extension = ['Dass', 'dass', 'Der', 'Die', 'Das', 'Dem', 'Den']
    for word in word_list_extension:
        stop_words.add(word)

    clean_without_stopwords = [word for word in liste_speech_word_tokenized if not word in stop_words]                       # herausfiltern der stopwords
    freq_Cleanded_without_stopwords =  FreqDist(clean_without_stopwords)                                        # Neuzuweisung: methode FreqDist() - Ermittlung der Vorkommenshaeufigkeit der Woerter im gesaeuberten RedeText ohne stopwords
    #freq_Cleanded_without_stopwords.tabulate()                                                                  # most high-frequency parts of speech
    complete_text_with_doubles_without_stopwords = list(freq_Cleanded_without_stopwords)
    diff_words_without_doubles = set(complete_text_with_doubles_without_stopwords)                              # "diff_words_without_doubles" enthaelt keine doppelten Woerter mehr
    #diversity_without_stopwords = len(diff_words_without_doubles) / float(len(complete_text_with_doubles_without_stopwords))

    print(freq_Cleanded_without_stopwords)
    list_seldom_words_without_stopwords, list_frequently_words_without_stopwords = count_seldom_frequently(freq_Cleanded_without_stopwords)  # Visualisieren der haufigsten und seltensten Woerter ohne stopwords
    print('rrrrrrrrrrrrrrrrr: ',list_seldom_words_without_stopwords)
    print('rrrrrrrrrrrrrrrrr: ',list_frequently_words_without_stopwords)
    name = "Redner: " + 'xxxxxxxxxxxxxxxxxxxx'
    print(name)
    #print("different words:    {0:8d}".format(len(diff_words)))                                    # Anzahl unterschiedlich einmalig genutzter Woerter
    #print("words:              {0:8d}".format(len(wordlist)))                                       # Anzahl genutzter Woerter
    #print("lexical diversity without stopwords:  {0:8.2f}".format(diversity_without_stopwords))     # Prozentsatz fuer die Sprachvielfalt ohne stopwords

    return list_seldom_words_without_stopwords, list_frequently_words_without_stopwords

def create_protocol_workbook(liste_dictionary_reden_einer_sitzung):
    # Create a workbook and add a worksheet.
    workbook = xlsxwriter.Workbook('bundestag_protokolle.xlsx')
    sitzungsdaten = workbook.add_worksheet('Sitzungsdaten')
    rededaten = workbook.add_worksheet('Rededaten')

    # Add a bold format to use to highlight cells.
    bold = workbook.add_format({'bold': 1})

    # Adjust the column width.
    sitzungsdaten.set_column(1, 1, 15)
    rededaten.set_column(1, 1, 15)

    # Write data headers.
    sitzungsdaten.write('A1', 'Sitzungsnummer', bold)
    sitzungsdaten.write('B1', 'Sitzungsdatum', bold)
    sitzungsdaten.write('C1', 'Wahlperiode', bold)
    sitzungsdaten.write('D1', 'Tagesordnungspunkt', bold)
    sitzungsdaten.write('E1', 'Tagesordnungspunktbezeichnung', bold)
    sitzungsdaten.write('F1', 'Redner', bold)
    sitzungsdaten.write('G1', 'rede_id_sitzungen', bold)

    rededaten.write('A1', 'rede_id', bold)
    rededaten.write('B1', 'clean_rede', bold)
    rededaten.write('C1', 'beifaelle', bold)
    rededaten.write('D1', 'anzahl_beifaelle', bold)
    rededaten.write('E1', 'wortmeldungen', bold)
    rededaten.write('F1', 'anzahl_wortmeldungen', bold)
    rededaten.write('G1', '10_seldom_words', bold)
    rededaten.write('H1', '10_frequently_words', bold)


    # writing in worksheet 'Sitzungsdaten'
    row = 1
    col = 0
    for dict in liste_dictionary_reden_einer_sitzung:
        for key in ['sitzungsnummer', 'sitzungsdatum', 'wahlperiode', 'tagesordnungspunkt', 'tagesordnungspunktbezeichnung', 'redner', 'rede_id_sitzungen']:
            if isinstance(dict[key], list):
                for item in dict[key]:
                    sitzungsdaten.write(row, col, item)
                    row += 1
                #col += 1
            else:
                sitzungsdaten.write(row, col, dict[key])
            col += 1
        row += 1
        col = 0

    # writing in worksheet 'Rededaten'
    row = 1
    row_listeneintrag = 1
    temp_row = 1
    col = 0
    for dict in liste_dictionary_reden_einer_sitzung:
        for key in ['rede_id', 'clean_rede', 'beifaelle', 'anzahl_beifaelle', 'wortmeldungen', 'anzahl_wortmeldungen', '10_seldom_words', '10_frequently_words']:
            if isinstance(dict[key], list):
                for item in dict[key]:
                    rededaten.write(row, col, item)
                    row += 1


            else:
                rededaten.write(temp_row, col, dict[key])
            col += 1
        row += 1
        temp_row += 1
        col = 0

    workbook.close()

def clean_speeches(alle_Reden_einer_Sitzung):
    '''
    Holt alle Zwischenrufe, Beifälle, Unruhe, etc. aus einer Rede
    :return: liste_dictionary_reden_einer_sitzung
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

        string_rede = ' '.join(rede)
        liste_treffer = re.findall(regex, string_rede)

        for i in liste_treffer:
            print('Eintrag: ',i)
            if i.__contains__('Beifall'):
                counter_beifaelle += 1
                liste_beifaelle.append(i)          # Hinzufügen aller Beifälle einer Rede
            else:
                counter_wortmeldungen += 1
                liste_wortmeldungen.append(i)  # Hinzufügen aller Wortmeldungen einer Rede

            string_rede = string_rede.replace('(' + i + ')', '')

        #string_beifaelle = ' ; '.join(liste_beifaelle)
        #string_wortmeldungen = ' ; '.join(liste_wortmeldungen)

        ### Analyse Redetext - Haufigkeit und lexikalische Diversitaet
        liste_speech_word_tokenized = speech_to_words_if_word_isalpha(string_rede)
        list_seldom_words_without_stopwords, list_frequently_words_without_stopwords = lex_div_without_stopwords(liste_speech_word_tokenized)
        string_seldom_words = ' ; '.join(list_seldom_words_without_stopwords)
        string_frequently_words = ' ; '.join(list_frequently_words_without_stopwords)

        result_dictionary_einer_rede = {
                                'sitzungsnummer'        : 'sss',
                                'sitzungsdatum'         : 'rrr',
                                'wahlperiode'           : 'fff',
                                'tagesordnungspunkt'    : 'zzz',
                                'tagesordnungspunktbezeichnung': 'dfdedf',
                                'redner'                : '234567',
                                'rede_id_sitzungen'     :   rede_id,
                                'rede_id'               :   rede_id,
                                'clean_rede'            :   string_rede,
                                'beifaelle'             :   liste_beifaelle,
                                'anzahl_beifaelle'      :   counter_beifaelle,
                                'wortmeldungen'         :   liste_wortmeldungen,
                                'anzahl_wortmeldungen'  :   counter_wortmeldungen,
                                '10_seldom_words'       :   string_seldom_words,
                                '10_frequently_words'   :   string_frequently_words

        }
        liste_dictionary_reden_einer_sitzung.append(result_dictionary_einer_rede)
        rede_id += 1
    return liste_dictionary_reden_einer_sitzung

### ENDE Testing_Steve ###


### START Testing_Marc ###

def start_scraping_with_chrome(url):
    '''
    Scrapt eine Webseite mit dem Google-Chrome-Browser anhand einer übergebenen URL
    :param url: String - URL
    :return: Selenium-Chrome-Webdriver-Objekt
    '''
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome = webdriver.Chrome('/usr/bin/chromedriver', chrome_options=chrome_options)
    chrome.get(url)
    return chrome

def get_new_zp_topic(topic):
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

    :param topic: Tagesordnungspunkt (z.B. 'TOP 40 Bundeswehreinsatz im Mittelmeer')
    :param whitespaces_to_jump: Spaces die es zu überspringen gilt, bis der Tagesordnungspunktname erreicht wurde (meistens 2)
    :return: z.B. 'TOP 40 Bundeswehreinsatz im Mittelmeer' wird übergeben mit whitespaces_to_jump = 2 -> returned 'TOP 40'
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

    :param top: z.B.: 'TOP 40'
    :param topic: z.B. 'TOP 40 Bundeswehreinsatz im Mittelmeer'
    :return: Tagesordnungspunkt-Beschreibung z.B.: 'Bundeswehreinsatz im Mittelmeer'
    '''
    topic_name = topic.replace(top, '')
    topic_name = topic_name.strip()
    return topic_name

def get_alle_tops_and_alle_sitzungen_from_soup(soup):
    '''
    Holt alle Tagesordnungspunkte und die Metadaten der vorhandenen Sitzungen aus der "Wundervollen Suppe"

    :param soup: Beautiful-Soup-Objekt
    :return: Dictionary - Mit allen unbearbeiteten TOPs (Liste); Sitzungsmetadaten (Dictionary)
    '''
    dict = {'num_Sitzung': '', 'num_Wahlperiode': '', 'dat_Sitzung': '', 'top': {}}
    liste_dict = []
    liste_top = []
    alle_tops_list = []

    for item in soup.find_all('strong'):
        # print(item.get_text())
        if item.get_text().__contains__('Wahlperiode'):
            dict = {'num_Sitzung': item.get_text()[7:10], 'num_Wahlperiode': item.get_text()[21:23],
                    'dat_Sitzung': item.get_text()[38:48]}
            liste_dict.append(dict)
        if item.get_text().__contains__('TOP'):
            # print(para.get_text())
            liste_top.append(item.get_text())
        alle_tops_list.append(item.get_text())
    return {'TOPs': alle_tops_list, 'Alle_Sitzungen': liste_dict}

def get_alle_sitzungen_mit_start_und_ende_der_topic(alle_tops_list, alle_sitzungen):
    '''
    Gibt alle Sitzungen zurück samt Topics, deren Rednern, sowie die Sitzungsmetadaten. (Sitzungsnummer, Datum, Wahlperiode)
    Vereint hierbei die unbearbeiteten Topics mit den Sitzungsmetadaten.

    :param alle_tops_list: Liste - Tgesordnungspunkte
    :param alle_sitzungen: Liste - Sitzungsmetadaten
    :return: Liste
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

    :param dict_topics:
    :return:
    '''
    if len(dict_topics) >1:
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

    :param alle_sitzungen:
    :return:
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
                        top_number_key += ' Topic_ID: ' + str(topic_id)
                        top_name = top_number_key
                    dict_topics[top_number_key] = {'Tagesordnungspunkt': top_name, 'TOP_ID':topic_id}

            else:

                list_redner.append(topic)

            if top_number_key != 'TOP':

                dict_topics[top_number_key]['Redner'] = list_redner
        list_sorted_topics = sort_dict_topics_via_topic_id(dict_topics)
        dict_sitzung = {
            'Sitzungsdatum': sitzungs_datum,
            'Wahlperiode': wahlperiode,
            'TOPs': list_sorted_topics
        }

        dict_sitzungen['Sitzung ' + sitzungs_nummer] = dict_sitzung

    return dict_sitzungen

def delete_first_and_last_speecher_from_list(dict_sitzungen):

    #for sitzung in sorted(dict_sitzungen):

    #temporär nur für eine Sitzung 240
    sitzung = 'Sitzung 240'
    temp_speecher_list = dict_sitzungen[sitzung]['TOPs']
    top_counter = 0
    while top_counter < len(temp_speecher_list):

        if len(temp_speecher_list[top_counter]['Redner']) >=3:
            temp_top_liste = temp_speecher_list[top_counter]['Redner']
            temp_top_liste.remove(temp_top_liste[0])
            temp_top_liste.remove(temp_top_liste[len(temp_top_liste) - 1])
            top_counter += 1

        elif len(temp_speecher_list[top_counter]['Redner']) < 3:
            del temp_speecher_list[top_counter]




    return dict_sitzungen

def sort_reden_eines_tops_in_tagesordnungspunkt(reden_eines_tops, top_counter, cleaned_sortierte_sitzungen, aktuelle_sitzungsbezeichnung):
    i = 0
    list_sorted_redner_temp =[]
    for redner in cleaned_sortierte_sitzungen[aktuelle_sitzungsbezeichnung]['TOPs'][top_counter]['Redner']:
        dict_temp_redner = {str(redner): reden_eines_tops[i]}
        list_sorted_redner_temp.append(dict_temp_redner)
        i += 1
    cleaned_sortierte_sitzungen[aktuelle_sitzungsbezeichnung]['TOPs'][top_counter]['Redner'] = list_sorted_redner_temp
    return cleaned_sortierte_sitzungen

def merge_sitzungsstruktur_mit_reden(redeliste, cleaned_sortierte_sitzung):

    aktuelle_sitzungsbezeichnung = 'Sitzung 240'
    aktuelle_sitzung = cleaned_sortierte_sitzungen['Sitzung 240']
    '''
    
    for sitzung in sorted(cleaned_sortierte_sitzungen):
        aktuelle_sitzungsbezeichnung = sitzung
        while aktuelle_sitzungsbezeichnung == 'Sitzung 229':
            aktuelle_sitzung = cleaned_sortierte_sitzungen[sitzung]

            i = 0
            for rede in redeliste:

                rede_id = rede['rede_id']

                if rede_id == aktuelle_sitzung['TOPs'][i]['TOP_ID']:
                    rede['wahlperiode'] = aktuelle_sitzung['Wahlperiode']
                    rede['sitzungsdatum'] = aktuelle_sitzung['Sitzungsdatum']
                    rede['tagesordnungspunktbezeichnung'] = aktuelle_sitzung['TOPs'][i]['Tagesordnungspunkt']
                    rede['tagesordnungspunkt'] = aktuelle_sitzung['TOPs'][i]['Top_Key']
                else:
                    print('###### Rede_ID passt nicht zur TOP_ID in merge_sitzungsstruktur_mit_reden()')
                redeliste[i] = rede
                i += 1
    '''

    laenge_der_redeliste = len(redeliste)
    tops = aktuelle_sitzung['TOPs']
    reden = redeliste
    j = 0
    top_counter = 0
    for top in tops:
        i = 0
        reden_eines_tagesordnungspunkts = []

        anzahl_redner_in_topic = len(tops[top_counter]['Redner'])
        print('Anzahl Redner in Tagesordnungspunkt "' + tops[top_counter]['Tagesordnungspunkt'] + '" : ' + str(anzahl_redner_in_topic))

        while i < anzahl_redner_in_topic:
            reden_eines_tagesordnungspunkts.append(reden.pop(0))
            i += 1
        if len(reden_eines_tagesordnungspunkts) > 1:
            final_cleaned_sortierte_sitzung = sort_reden_eines_tops_in_tagesordnungspunkt(reden_eines_tagesordnungspunkts, j, cleaned_sortierte_sitzung, aktuelle_sitzungsbezeichnung)
            j += 1
            top_counter += 1
        else:
            aktueller_tagesordnungspunkt = cleaned_sortierte_sitzungen[aktuelle_sitzungsbezeichnung]['TOPs'][top_counter]['Tagesordnungspunkt']
            print('Weniger als zwei Redner in Rednerliste des Tagesordnungspunktes "' + aktueller_tagesordnungspunkt + '". Tagesordnungspunkt wird gelöscht.')
            j += 1
            top_counter += 1

    return final_cleaned_sortierte_sitzung

def count_speecher():
    anz_redner = 0
    i = 0
    for top in temp_speecher_list:
        temp_top_liste.append(temp_speecher_list[i]['Redner'])
        anz_redner += len(temp_speecher_list[i]['Redner'])
        i +=1
    return str(anz_redner)

def count_speecher_from_cleaned_sortierte_sitzung(sitzung):
    result = 0
    for anz_redner_je_topic in sitzung['TOPs']:
        result += len(anz_redner_je_topic['Redner'])
    return result
#    for rede in reden_eines_tagesordnungspunkts:
#        for list_eintrag_redner in tops[top]['Redner']:
#            redner = {list_eintrag_redner:rede}

### ENDE Testing_Marc ###

### Start Using Functions Steve
content = get_content()
names_of_entities = split_and_analyse_content(content)
start_end_nummern_liste = get_start_and_end_of_a_speech()
liste_alle_reden = get_all_speeches(start_end_nummern_liste)

#print(start_end_nummern_liste)
redeliste = clean_speeches(liste_alle_reden)
#print(redeliste)
### ENDE Using Functions Steve

### START Using Functions Marc
chrome = start_scraping_with_chrome('http://www.bundestag.de/ajax/filterlist/de/dokumente/protokolle/-/442112/h_6810466be65964217012227c14bad20f?limit=1')
soup = BeautifulSoup(chrome.page_source, 'lxml')
alle_tops_und_alle_sitzungen = get_alle_tops_and_alle_sitzungen_from_soup(soup)

alle_tops_list = alle_tops_und_alle_sitzungen['TOPs']
alle_sitzungen = alle_tops_und_alle_sitzungen['Alle_Sitzungen']
alle_sitzungen_mit_start_und_ende_der_topic = get_alle_sitzungen_mit_start_und_ende_der_topic(alle_tops_list, alle_sitzungen)
sortierte_sitzungen = sort_topics_to_sitzung(alle_sitzungen_mit_start_und_ende_der_topic)
cleaned_sortierte_sitzungen = delete_first_and_last_speecher_from_list(sortierte_sitzungen)

print('Scraping beendet')
sitzung_240 = cleaned_sortierte_sitzungen['Sitzung 240']
anzahl_redner = count_speecher_from_cleaned_sortierte_sitzung(sitzung_240)
print('Anzahl Redner: ' + str(anzahl_redner))
### ENDE Using Functions Marc

### START spaßige teil###
'''
START Test 
'''
#sitzung_229 = cleaned_sortierte_sitzungen['Sitzung 229']
#temp_speecher_list = sitzung_229['TOPs']
temp_top_liste = []



#print("Anzahl einsortierte Redner: " + count_speecher())
print("Anzahl vorhandene Reden in Redeliste: " + str(len(redeliste)))
#print(len(temp_top_liste))
#print(temp_top_liste)

#merged_sitzung = merge_sitzungsstruktur_mit_reden(redeliste, sitzung_229)
mergeed_sitzung = merge_sitzungsstruktur_mit_reden(redeliste, cleaned_sortierte_sitzungen)
create_protocol_workbook(redeliste)
print('Skript "Vereinigung" beendet')