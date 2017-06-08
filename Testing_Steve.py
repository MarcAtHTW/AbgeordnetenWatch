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
import xlrd
import os
os.environ['JAVAHOME'] = "C:/Program Files/Java/jdk1.8.0_20/bin/java.exe"

'''
    Data extracting from Plenarprotokoll
'''

cleanList = []
start_Element_Rede = 0
list_with_startelement_numbers = []     # enthält Start item aller Redetexte
list_with_startEnd_numbers = []         # enthält Start und Ende item aller Redetexte
number_of_last_element = 0
list_elements_till_first_speech = []    # enthält listenelemente bis zur ersten Rede
dict_entity_polname_partyname = {}
temp_dict_entity_polname_partyname = {}
politican_name = ""
party_name = ""
dict_liste = []

''' get content fuer alle Seiten im Protokoll '''
def getContent():
    pdf_file = open('Plenarprotokoll_18_232.pdf', 'rb')
    read_pdf = PyPDF2.PdfFileReader(pdf_file)
    page_content = ''
    for i in range(read_pdf.getNumPages()):
        print(i)
        pages = read_pdf.getPage(i)
        page_content += pages.extractText()
    # text =open('18232-data.txt','rb')
    # page_content = ''
    # for line in text:
    #     print(line)
    #     page_content += str(line)

    return page_content
'''
- function fuer content-splitt und vorhalten in Liste
- Dabei entfernen von "\n" und "-" aus Listenelemente
- zusätzliche Speicherung in txt-file
'''
def contentToDict(page_content):
    list = sent_tokenize(page_content)
    # list = page_content.split(' ')
    print(list)
    for i in range(len(list)):
        list_element = list[i]
        list_element = list_element.replace("\n", "")
        list_element = list_element.replace("-", "")
        cleanList.append(list_element) # liste ohne -, \n
        #print("item at index", i, ":", list_element)       # alle Listenelemente

        analyse_list_element(list_element, i)
        set_number(i)

def set_number(i):
    global number_of_last_element
    number_of_last_element = i

def get_number():
    global number_of_last_element
    return number_of_last_element

''' analysiere Struktur list_element '''
''' Präsident Lammert übergibt "das Wort"... -> Name und Politiker '''
def analyse_list_element(list_element, i):
    temp_dict_empty_values = {'polName': '', 'partyName': ''}
    matchers = ['Das Wort','das Wort','nächste Redner','nächster Redner','nächste Rednerin','spricht jetzt','Nächste Rednerin','Nächster Redner' ,'Letzter Redner', 'nächste Wortmeldung']
    if any(m in list_element for m in matchers):
        print("\nWechsel Redner", i, ":", list_element)    # Listenelemente, die matchers enthalten
        start_Element_Rede = i + 1
        list_with_startelement_numbers.append(start_Element_Rede)
        print("Start_Index_Redetext: ", start_Element_Rede)

        '''- POS -> PartOfSpeech Verben, Nomen, ... in Listenelement mit matchers'''
        words = word_tokenize(list_element)
        '''extracting Named Entities - Person, Organization,...'''
        jar = 'jars\stanford-postagger.jar'
        model = 'jars\german-hgc.tagger'
        pos_tagger = StanfordPOSTagger(model, jar, encoding='utf8')
        tagged = pos_tagger.tag(words)
        print(tagged)
        chunkGram = r"""Eigenname: {<NE>?}"""
        chunkParser = nltk.RegexpParser(chunkGram)
        namedEnt = chunkParser.parse(tagged)
        print("chunkParser: ",namedEnt)
        #namedEnt.draw()
        ''' extract entity names - anhand von label - NE => Eigenname'''
        entityPers_names_subtree = []
        for subtree in namedEnt.subtrees(filter=lambda t: t.label() == 'Eigenname'):
            print(subtree)
            entityPers_names_subtree.append(subtree[0])
        print('entityPers_names_subtree: ',entityPers_names_subtree)
        entityPers_names = []
        name = ''
        for ne in entityPers_names_subtree:
            name += ' ' + ne[0]
        entityPers_names.append(name)
        print("Person: ",entityPers_names)
        print("Person:",str(name))

        # Abfrage: Leeres oder gefülltes Dict ( Namen und Partei)
        temp_dict_entity_polname_partyname = check_name_party_in_xls(entityPers_names)
        print('dictionary: ', temp_dict_entity_polname_partyname)

        # Hinzufügen von leeren und gefüllten Dict in dict_liste
        dict_liste.append(temp_dict_entity_polname_partyname)
        print('dict_liste: ', dict_liste)

    # Listenelement ist entweder 'Anfang bis zur ersten Rede' oder 'Redeteil'
    else:
        Rede = []
        if len(list_with_startelement_numbers) != 0:        # wenn bereits eine Startnummer (erste Rede) vorhanden
            print("Redeteil:", i, list_element)
        else:
            global list_elements_till_first_speech
            list_elements_till_first_speech.append(list_element)  # Teile mit TOP, ZTOP,...
            print('global-> erste Zeilen: ', list_element)


''' Abgleich mit Excelcheet'''
def check_name_party_in_xls(namesOfEntities):
    temp_dict_entity_polname_partyname = {'polName': '', 'partyName': ''}
    print('Abgleich pos-Name mit EXCEL-Eintrag')
    politican_name = ''
    party_name = ''
    ''' Excel-sheet with all politicans '''
    workbook = xlrd.open_workbook('mdb.xls')
    worksheet = workbook.sheet_by_name('Tabelle1')
    first_col_Names = worksheet.col_values(0)  # Spalte mit Namen, die KEINE Bindestriche enthalten
    second_col_Names = worksheet.col_values(1)  # Spalte mit Namen, die Bindestriche enthalten
    third_col_Party = worksheet.col_values(2)
    #print(first_col_Names)
    #print(second_col_Names)
    #print(third_col_Party)
    matchers = first_col_Names
    for i in range(len(namesOfEntities)):
        name = namesOfEntities[i]
        for m in range(len(matchers)):
            matcher_element = matchers[m]
            if matcher_element.__contains__(name) or name.__contains__(matcher_element):
                print("listen_eintrag", i, ": ", name)
                print("excel_eintrag_name", m, ": ", matcher_element)
                print("excel_eintrag_name_mit_Bindestrich", m, ": ", second_col_Names[m])
                print("excel_eintrag_partei", m, ": ", third_col_Party[m])
                politican_name = second_col_Names[m]
                party_name = third_col_Party[m]
                temp_dict_entity_polname_partyname = {'polName': politican_name, 'partyName': party_name}
                print('wwwwwwwwwwwwwwwwwwwwwwww: ',temp_dict_entity_polname_partyname['polName'])
                print('wwwwwwwwwwwwwwwwwwwwwwww: ',temp_dict_entity_polname_partyname['partyName'])

                ''' Eintrag in DB Name + Partei'''

    # Rückgabe eine leeren Dict oder gefüllten Dict, falls Excel-Eintrag vorhanden ist
    return temp_dict_entity_polname_partyname


''' Anbindung API-Abgeordnetenwatch - JSON Data-Extract'''
# def api_json():
#     import urllib.request, json
#     politican_name = politican_name.lower()
#     print(politican_name)
#     politican_name = politican_name.replace(' ','-')
#     print(politican_name)
#     with urllib.request.urlopen("https://www.abgeordnetenwatch.de/api/profile/"+politican_name+"/profile.json") as url:
#         data = json.loads(url.read().decode())
#         print(data)
#         print(data['profile']['personal']['first_name']+ " " +data['profile']['personal']['last_name'])
#         print(data['profile']['party'])
#
#     ''' Eintrag in DB Name + Partei'''


content = getContent()
namesOfEntities = contentToDict(content)


''' Bestimmung von Start und Ende der Reden'''

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

i = 0
while i <= len(list_with_startelement_numbers)-1:
    liste_mit_Startnummern_und_End.append(list_with_startelement_numbers[i])
    liste_mit_Startnummern_und_End.append(liste_mit_Endnummern[i])
    i += 1
print('Liste mit Start-und Endnummern: ',liste_mit_Startnummern_und_End)
print(len(liste_mit_Startnummern_und_End))

''' alle Reden in einer Liste halten'''

alle_Reden = []
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
        alle_Reden.append(cleanList[liste_mit_Startnummern_und_End[x]:liste_mit_Startnummern_und_End[y]])  # [alle zwischen Start:Ende]
        #print("weiter")
        #print("start: ", start)
    x += 2
    y += 2
    start += 2
print(len(alle_Reden))
print(len(dict_liste))

# Ausgabe aller Reden
for rede in alle_Reden:
    print(rede)

''' Redeteil einem dict zuordnen in dict_liste'''
x= 0
for dict in dict_liste:
    dict['rede'] = alle_Reden[x]
    x += 1
for dict in dict_liste:
    print(dict)
    print(dict['polName'])
    print(dict['partyName'])
    print(dict['rede'])




    ''' DB-Eintrag für Politiker-Rede'''
    ''' enthält noch Beifall/ Zwischenrufe'''

    print("\n")

# matchers = ['...']
# for element in list_elements_till_first_speech():
#     if matchers in element:
#         print(element)






''' xxxxxxxxxxxxxxxxxxxxxxxxxxx   Datenbank befuellen   xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx '''









''' xxxxxxxxxxxxxxxxxxxxxxxxx   Analyse Redetext - Haufigkeit und lexikalische Diversitaet   xxxxxxxxxxxxxxxxxxxxxxxxxxxx '''

def clean_and_getFrequenz(wordlist):
    words = word_tokenize(str(wordlist))
    # RedeText enthealt noch  „!“, „,“, „.“ und Doppelungen und so weiter
    print("Anzahl aller Woerter und Zeichen: " + str(len(words)))
    # saebern des RedeTextes von Zeichen !!! ABER !!! doppelte Woerter lassen, da die Haeufigkeit spaeter gezaehlt werden soll
    cleaned_speech = [word for word in words if word.isalpha()]
    print("Anzahl aller Woerter - AUCH DOPPELTE ohne Zeichen: " + str(len(cleaned_speech)))
    return cleaned_speech

def count_and_viz_seldom_frequently(freq_CleandedSpeech):
    # 30 haeufigsten und seltensten Woerter einer gesaeuberten Rede
    dc_sort = (sorted(freq_CleandedSpeech.items(), key= operator.itemgetter(1), reverse = True))   # sortiertes dictionary - beginnend mit groeßter Haeufigkeit
    print(dc_sort[:30])                         # 30 haeufigsten Woerter (Wort: Anzahl)
    print([str(w[0]) for w in dc_sort[:30]])    # 30 haeufigsten Woerter (nur Wort)
    print(dc_sort[-30:])                        # 30 seltensten Woerter (Wort: Anzahl)
    print([str(w[0]) for w in dc_sort[-30:]])   # 30 seltensten Woerter (nur Wort)

    # Wir koennen uns auch eine kummulative Verteilungsfunktion grafisch anzeigen lassen. Dazu können wir die plot()-Methode
    # auf dem fdist1-Objekt anwenden. Dazu muss jedoch das Modul matplotlib installiert sein!
    freq_CleandedSpeech.plot(30, cumulative=True)

def lex_div_with_and_without_stopwords(wordlist, cleaned_speech):
    ###### Lexikalische Diversität eines Redners - Vielzahl von Ausdrucksmöglichkeiten #######
    # Die Diversität ist ein Maß für die Sprachvielfalt. Sie ist definiert als Quotient der „verschiedenen Wörter“ dividiert durch die „Gesamtanzahl von Wörtern“ eines Textes.

    # Redetext mit stop words
    freq_CleandedSpeech_with_stopwords = FreqDist(cleaned_speech)           # methode FreqDist() - Ermittlung der Vorkommenshaeufigkeit der Woerter im gesaeuberten RedeText
    print(freq_CleandedSpeech_with_stopwords)
    #freq_CleandedSpeech_with_stopwords.tabulate()                           # most high-frequency parts of speech
    count_and_viz_seldom_frequently(freq_CleandedSpeech_with_stopwords)     # Visualisieren der haufigsten und seltensten Woerter inclusive stopwords

    complete_text_with_doubles = list(freq_CleandedSpeech_with_stopwords)        # noch doppelte Woerter enthalten
    diff_words = set(complete_text_with_doubles)                                 # "diff_words" enthaelt keine doppelten Woerter mehr
    diversity_with_stopwords = len(diff_words) / float(len(complete_text_with_doubles))

    # Redetext ohne stop words
    stop_words = set(stopwords.words("german"))
    print("\n" + "STOPWORDS: " + "\n" + str(stop_words) + "\n")

    clean_without_stopwords = [word for word in cleaned_speech if not word in stop_words]                       # herausfiltern der stopwords
    freq_Cleanded_without_stopwords =  FreqDist(clean_without_stopwords)                                        # Neuzuweisung: methode FreqDist() - Ermittlung der Vorkommenshaeufigkeit der Woerter im gesaeuberten RedeText ohne stopwords
    #freq_Cleanded_without_stopwords.tabulate()                                                                  # most high-frequency parts of speech
    complete_text_with_doubles_without_stopwords = list(freq_Cleanded_without_stopwords)
    diff_words_without_doubles = set(complete_text_with_doubles_without_stopwords)                              # "diff_words_without_doubles" enthaelt keine doppelten Woerter mehr
    diversity_without_stopwords = len(diff_words_without_doubles) / float(len(complete_text_with_doubles_without_stopwords))

    print(freq_Cleanded_without_stopwords)
    count_and_viz_seldom_frequently(freq_Cleanded_without_stopwords)  # Visualisieren der haufigsten und seltensten Woerter ohne stopwords

    name = "Redner: " + 'xxxxxxxxxxxxxxxxxxxx'
    print(name)
    print("different words:    {0:8d}".format(len(diff_words)))                                     # Anzahl unterschiedlich einmalig genutzter Woerter
    print("words:              {0:8d}".format(len(wordlist)))                                       # Anzahl genutzter Woerter
    print("lexical diversity with stopwords:  {0:8.2f}".format(diversity_with_stopwords))           # Prozentsatz fuer die Sprachvielfalt mit stopwords
    print("lexical diversity without stopwords:  {0:8.2f}".format(diversity_without_stopwords))     # Prozentsatz fuer die Sprachvielfalt ohne stopwords

# cleaned_Speech = clean_and_getFrequenz(wordlist)
# lex_div_with_and_without_stopwords(wordlist, cleaned_Speech)
