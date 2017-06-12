from selenium import webdriver
from bs4 import BeautifulSoup
import os

def start_scraping_with_chrome(url):
    '''
    Scrapt eine Webseite mit dem Google-Chrome-Browser anhand einer übergebenen URL
    :param url: String - URL
    :return: Selenium-Chrome-Webdriver-Objekt
    '''
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome = webdriver.Chrome('C:/Python36-32/BrowserDriver/chromedriver.exe', chrome_options=chrome_options)
    chrome.get(url)

    return chrome

def rebuild_topic(topic, whitespaces_to_jump):
    '''
    Nimmt den Tagesordnungspunkt auseinander und gibt den 'TOP X' zurück

    :param topic: Tagesordnungspunkt (z.B. 'TOP 40 Bundeswehreinsatz im Mittelmeer')
    :param whitespaces_to_jump: Spaces die es zu überspringen gilt, bis der Tagesordnungspunktname erreicht wurde (meistens 2)
    :return: z.B. 'TOP 40 Bundeswehreinsatz im Mittelmeer' wird übergeben mit whitespaces_to_jump = 2 -> returned 'TOP 40'
    '''
    found_spaces = 0
    new_topic = ''
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
    alle_tops_list =[]

    for item in soup.find_all('strong'):
        #print(item.get_text())
        if item.get_text().__contains__('Wahlperiode'):
            dict = {'num_Sitzung': item.get_text()[7:10], 'num_Wahlperiode': item.get_text()[21:23], 'dat_Sitzung': item.get_text()[38:48]}
            liste_dict.append(dict)
        if item.get_text().__contains__('TOP'):
            #print(para.get_text())
            liste_top.append(item.get_text())
        alle_tops_list.append(item.get_text())
    return {'TOPs' : alle_tops_list, 'Alle_Sitzungen':liste_dict}

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

def sort_topics_to_sitzung(alle_sitzungen):
    '''
    Bearbeitet die Tagesordnungspunkte, sortiert die Redner den entsprechenden Tagesordnungspunkten zu. Zuordnung der
    Sitzungs-Metadaten in die entsprechende Sitzung.

    :param alle_sitzungen:
    :return:
    '''
    dict_sitzungen = {}

    for sitzung in alle_sitzungen:
        tops            = sitzung['top'][0]
        sitzungs_datum  = sitzung['dat_Sitzung']
        wahlperiode     = sitzung['num_Wahlperiode']
        sitzungs_nummer = sitzung['num_Sitzung']

        tops.index
        dict_rede       = {}
        dict_sitzung    = {}
        list_redner     = []
        top_counter     = -1

        top_zwischenspeicher = ''
        dict_topics = {}
        for i in range(len(tops)):

            topic = tops[i]
            topic = topic.strip()

            #print(topic)
            if topic.__contains__('TOP'):
                top_counter = top_counter +1
                list_redner = []

                top_number_key  = rebuild_topic(topic, 2)
                top_name        = get_topic_name_from_topic_number(top_number_key, topic)
                dict_topics[top_number_key] = {'Tagesordnungspunkt': top_name}

            else:
                '''
                Füge alle Redner einer Topic, der entsprechenden Topic hinzu, prüfe jedoch vorher, ob sich der jeweilige
                Redner bereits in der Liste befindet und füge ihn nur hinzu, sofern er noch nicht drin ist.
                '''
                allready_in_list = False
                for redner in list_redner:
                    if redner == topic:
                        allready_in_list = True
                if allready_in_list == False:
                    list_redner.append(topic)

            dict_topics[top_number_key]['Redner'] = list_redner

        dict_sitzung = {
                        'Sitzungsdatum' : sitzungs_datum,
                        'Wahlperiode'   : wahlperiode,
                        'TOPs'           : dict_topics
                    }

        dict_sitzungen['Sitzung ' + sitzungs_nummer] = dict_sitzung

    return dict_sitzungen


chrome = start_scraping_with_chrome('http://www.bundestag.de/ajax/filterlist/de/dokumente/protokolle/-/442112/h_6810466be65964217012227c14bad20f?limit=1')
soup=BeautifulSoup(chrome.page_source,'lxml')
alle_tops_und_alle_sitzungen = get_alle_tops_and_alle_sitzungen_from_soup(soup)

alle_tops_list = alle_tops_und_alle_sitzungen['TOPs']
alle_sitzungen = alle_tops_und_alle_sitzungen['Alle_Sitzungen']

alle_sitzungen_mit_start_und_ende_der_topic = get_alle_sitzungen_mit_start_und_ende_der_topic(alle_tops_list, alle_sitzungen)

sortierte_sitzungen = sort_topics_to_sitzung(alle_sitzungen_mit_start_und_ende_der_topic)

print('test')
