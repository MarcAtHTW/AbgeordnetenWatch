"""
@author: Steve
"""
import PyPDF2
import nltk
from nltk import FreqDist
from nltk.corpus import stopwords
import operator
from nltk import sent_tokenize, word_tokenize
from nltk import StanfordPOSTagger
import os
import xlsxwriter
import re
import codecs
os.environ['JAVAHOME'] = "C:/Program Files/Java/jdk1.8.0_20/bin/java.exe"

'''
    Data extracting from Plenarprotokoll
'''
''' Globals '''
indexierte_liste = []                          # Vorhalten von Redeteilen
start_Element_Rede = 0
list_with_startelement_numbers = []     # enthält Start item aller Redetexte
list_with_startEnd_numbers = []         # enthält Start und Ende item aller Redetexte
number_of_last_element = 0
list_elements_till_first_speech = []    # enthält listenelemente bis zur ersten Rede
politican_name = ""
party_name = ""
ende_der_letzten_rede = 0
start_der_ersten_rede = 0



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
        #list_element = list_element.replace("\n", "")
        #list_element = list_element.replace("-", "")
        indexierte_liste.append(list_element) # liste ohne -, \n
        #print("item at index", i, ":", list_element)       # alle Listenelemente
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
    politican_name = politican_name.replace(' ','-')
    with urllib.request.urlopen("https://www.abgeordnetenwatch.de/api/profile/"+politican_name+"/profile.json") as url:
        data = json.loads(url.read().decode())
        politiker_name = data['profile']['personal']['first_name']+ " " +data['profile']['personal']['last_name']
        partei = data['profile']['party']
    return politican_name, partei

def get_start_and_end_of_a_speech():
    '''
    Bestimmung von Start und Ende der Reden
    :return: Liste mit Liste mit Start-und Endnummern
    '''
    print("Liste mit Startnummern: ",list_with_startelement_numbers)
    print(len(list_with_startelement_numbers))
    liste_mit_Startnummern_und_End = []
    liste_mit_Endnummern = []
    i = 0
    x= 1
    while i < len(list_with_startelement_numbers)-1:
        liste_mit_Endnummern.insert(i, list_with_startelement_numbers[x]-1)
        if i == len(list_with_startelement_numbers) - 2:
            liste_mit_Endnummern.append(get_number())
        i += 1
        x += 1
    print('Liste mit Endnummern: ',liste_mit_Endnummern)
    print(len(liste_mit_Endnummern))
    # Füllen mit Start und Endnummern
    i = 0
    while i <= len(list_with_startelement_numbers)-1:
        liste_mit_Startnummern_und_End.append(list_with_startelement_numbers[i])
        liste_mit_Startnummern_und_End.append(liste_mit_Endnummern[i])
        i += 1


    #liste_mit_Startnummern_und_End[0] = start_der_ersten_rede
    del liste_mit_Startnummern_und_End[-1]
    liste_mit_Startnummern_und_End.append(ende_der_letzten_rede)

    print('Liste mit Start-und Endnummern: ',liste_mit_Startnummern_und_End)
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
    end = len(liste_mit_Startnummern_und_End)-1
    active = True
    while active:
        print("x: ", x)
        print("y: ", y)
        print("start: ", start)
        if start > end:
            active = False
            print("false")
        else:
            alle_Reden_einer_Sitzung.append(indexierte_liste[liste_mit_Startnummern_und_End[x]:liste_mit_Startnummern_und_End[y]])  # [alle zwischen Start:Ende]
        x += 2
        y += 2
        start += 2
    print(len(alle_Reden_einer_Sitzung))
    # Ausgabe aller Reden
    #for rede in alle_Reden_einer_Sitzung:
        #print(rede)
    return alle_Reden_einer_Sitzung

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
                                '10_seldom_words'       :   list_seldom_words_without_stopwords,
                                '10_frequently_words'   :   list_frequently_words_without_stopwords

        }
        liste_dictionary_reden_einer_sitzung.append(result_dictionary_einer_rede)
        rede_id += 1
    return liste_dictionary_reden_einer_sitzung


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
    topdaten = workbook.add_worksheet('Topdaten')
    redner_rede_daten = workbook.add_worksheet('Redner_Rede')
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
    beifalldaten.set_column(1, 1, 15)
    wortmeldedaten.set_column(1, 1, 15)
    seldom_words_daten.set_column(1, 1, 15)
    freq_words_daten.set_column(1, 1, 15)

    # Write data headers.
    sitzungsdaten.write('A1', 'Sitzungsnummer', bold)
    sitzungsdaten.write('B1', 'Sitzungsdatum', bold)
    sitzungsdaten.write('C1', 'Wahlperiode', bold)

    topdaten.write('A1', 'Sitzungsnummer', bold)
    topdaten.write('B1', 'Tagesordnungspunkt', bold)
    topdaten.write('C1', 'Tagesordnungspunktbezeichnung', bold)

    redner_rede_daten.write('A1', 'Tagesordnungspunktbezeichnung', bold)
    redner_rede_daten.write('B1', 'Redner', bold)
    redner_rede_daten.write('C1', 'clean_rede', bold)
    redner_rede_daten.write('D1', 'rede_id', bold)

    beifalldaten.write('A1', 'rede_id', bold)
    beifalldaten.write('B1', 'Beifalltext', bold)

    wortmeldedaten.write('A1', 'rede_id', bold)
    wortmeldedaten.write('B1', 'Wortmeldungen', bold)

    seldom_words_daten.write('A1', 'rede_id', bold)
    seldom_words_daten.write('B1', 'Seldom_words', bold)

    freq_words_daten.write('A1', 'rede_id', bold)
    freq_words_daten.write('B1', 'freq_words', bold)

    # writing in worksheet 'Sitzungsdaten'
    row = 1
    col = 0
    for dict in liste_dictionary_reden_einer_sitzung:
        for key in ['sitzungsnummer', 'sitzungsdatum', 'wahlperiode']:
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

    # writing in worksheet 'Topdaten'
    row = 1
    col = 0
    for dict in liste_dictionary_reden_einer_sitzung:
        for key in ['sitzungsnummer', 'tagesordnungspunkt', 'tagesordnungspunktbezeichnung']:
            if isinstance(dict[key], list):
                for item in dict[key]:
                    topdaten.write(row, col, item)
                    row += 1
                #col += 1
            else:
                topdaten.write(row, col, dict[key])
            col += 1
        row += 1
        col = 0

    # writing in worksheet 'Redner_Rede'
    row = 1
    temp_row = 1
    col = 0
    for dict in liste_dictionary_reden_einer_sitzung:
        for key in ['tagesordnungspunktbezeichnung', 'redner', 'clean_rede', 'rede_id_sitzungen']:
            if isinstance(dict[key], list):
                for item in dict[key]:
                    redner_rede_daten.write(row, col, item)
                    row += 1
            else:
                k = 0
                while k < len(dict['beifaelle']):
                    redner_rede_daten.write(temp_row, col, dict[key])
                    k += 1
                    temp_row += 1
            col += 1
        col = 0




    # writing in worksheet 'Beifalldaten'
    row = 1
    temp_row = 1
    col = 0
    for dict in liste_dictionary_reden_einer_sitzung:
        for key in ['rede_id_sitzungen', 'beifaelle']:
            if isinstance(dict[key], list):
                for item in dict[key]:
                    beifalldaten.write(row, col, item)
                    row += 1
            else:
                k = 0
                while k < len(dict['beifaelle']):
                    beifalldaten.write(temp_row, col, dict[key])
                    k += 1
                    temp_row += 1
            col += 1
        col = 0

    # writing in worksheet 'Wortmeldedaten'
    row = 1
    temp_row = 1
    col = 0
    for dict in liste_dictionary_reden_einer_sitzung:
        for key in ['rede_id_sitzungen', 'wortmeldungen']:
            if isinstance(dict[key], list):
                for item in dict[key]:
                    wortmeldedaten.write(row, col, item)
                    row += 1
            else:
                k = 0
                while k < len(dict['wortmeldungen']):
                    wortmeldedaten.write(temp_row, col, dict[key])
                    k += 1
                    temp_row += 1
            col += 1
        col = 0

    # writing in worksheet 'seldom_words_daten'
    row = 1
    temp_row = 1
    col = 0
    for dict in liste_dictionary_reden_einer_sitzung:
        for key in ['rede_id_sitzungen', '10_seldom_words']:
            if isinstance(dict[key], list):
                for item in dict[key]:
                    seldom_words_daten.write(row, col, item)
                    row += 1
            else:
                k = 0
                while k < len(dict['10_seldom_words']):
                    seldom_words_daten.write(temp_row, col, dict[key])
                    k += 1
                    temp_row += 1
            col += 1
        col = 0

    # writing in worksheet 'freq_words_daten'
    row = 1
    temp_row = 1
    col = 0

    for dict in liste_dictionary_reden_einer_sitzung:
        for key in ['rede_id_sitzungen', '10_frequently_words']:
            if isinstance(dict[key], list):
                for item in dict[key]:
                    freq_words_daten.write(row, col, item)
                    row += 1
            else:
                k = 0
                while k < len(dict['10_frequently_words']):
                    freq_words_daten.write(temp_row, col, dict[key])
                    k += 1
                    temp_row += 1
            col += 1
        col = 0

    # row = 1
    # row_folge_dict = 1
    # liste_mit_hoechster_laenge = 0
    # temp_row = 1
    # col = 0
    # nr_dict = 0
    # for dict in liste_dictionary_reden_einer_sitzung:
    #
    #     if dict == liste_dictionary_reden_einer_sitzung[0]:
    #         print('true')
    #         for key in ['rede_id', 'clean_rede', 'beifaelle', 'anzahl_beifaelle', 'wortmeldungen', 'anzahl_wortmeldungen', '10_seldom_words', '10_frequently_words']:
    #             if key == 'beifaelle':
    #                 row = 1
    #                 for item in dict[key]:
    #                     rededaten.write(row, col, item)
    #                     row += 1
    #             elif key == 'wortmeldungen':
    #                 row = 1
    #                 for item in dict[key]:
    #                     rededaten.write(row, col, item)
    #                     row += 1
    #             elif key == '10_seldom_words':
    #                 row = 1
    #                 for item in dict[key]:
    #                     rededaten.write(row, col, item)
    #                     row += 1
    #             elif key == '10_frequently_words':
    #                 row = 1
    #                 for item in dict[key]:
    #                     rededaten.write(row, col, item)
    #                     row += 1
    #             else:
    #                 rededaten.write(1, col, dict[key])
    #             col += 1
    #
    #     if dict != liste_dictionary_reden_einer_sitzung[0]:
    #
    #         l_beifaelle = len(liste_dictionary_reden_einer_sitzung[nr_dict].get('beifaelle'))
    #         print('Laenge beifaelle: ', l_beifaelle)
    #         l_wortmeldungen = len(liste_dictionary_reden_einer_sitzung[nr_dict].get('wortmeldungen'))
    #         print('Laenge wortmeldungen: ', l_wortmeldungen)
    #         if l_beifaelle > l_wortmeldungen and l_beifaelle > 10:
    #             row_folge_dict += l_beifaelle
    #         elif l_wortmeldungen > l_beifaelle and l_wortmeldungen > 10:
    #             row_folge_dict += l_wortmeldungen
    #         elif l_beifaelle == l_wortmeldungen and l_beifaelle > 10:
    #             row_folge_dict += l_beifaelle
    #         elif l_beifaelle == l_wortmeldungen and l_beifaelle < 10:
    #             row_folge_dict += 10
    #         else:
    #             row_folge_dict += 10
    #
    #         print(row_folge_dict)
    #         temp_row = row_folge_dict
    #         row_beifaelle = row_folge_dict
    #         row_meldungen = row_folge_dict
    #         row_seldom = row_folge_dict
    #         row_frequently = row_folge_dict
    #         nr_dict += 1
    #
    #         for key in ['rede_id', 'clean_rede', 'beifaelle', 'anzahl_beifaelle', 'wortmeldungen', 'anzahl_wortmeldungen', '10_seldom_words', '10_frequently_words']:
    #             if key == 'beifaelle':
    #                 for item in dict[key]:
    #                     rededaten.write(row_beifaelle, col, item)
    #                     row_beifaelle += 1
    #             elif key == 'wortmeldungen':
    #                 for item in dict[key]:
    #                     rededaten.write(row_meldungen, col, item)
    #                     row_meldungen += 1
    #             elif key == '10_seldom_words':
    #                 for item in dict[key]:
    #                     rededaten.write(row_seldom, col, item)
    #                     row_seldom += 1
    #             elif key == '10_frequently_words':
    #                 for item in dict[key]:
    #                     rededaten.write(row_frequently, col, item)
    #                     row_frequently += 1
    #             else:
    #                 rededaten.write(temp_row, col, dict[key])
    #             col += 1
    #     col = 0

    workbook.close()



content = get_content()
names_of_entities = split_and_analyse_content(content)
start_end_nummern_liste = get_start_and_end_of_a_speech()
liste_alle_reden = get_all_speeches(start_end_nummern_liste)

print(start_end_nummern_liste)
redeliste = clean_speeches(liste_alle_reden)
#print(redeliste)
create_protocol_workbook(redeliste)


