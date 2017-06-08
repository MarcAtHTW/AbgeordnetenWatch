from selenium import webdriver


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome = webdriver.Chrome('/usr/bin/chromedriver', chrome_options=chrome_options)
chrome.get('http://www.bundestag.de/ajax/filterlist/de/dokumente/protokolle/-/442112/h_6810466be65964217012227c14bad20f?limit=1')

from bs4 import BeautifulSoup

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

soup=BeautifulSoup(chrome.page_source,'lxml')

dict = {'num_Sitzung': '', 'num_Wahlperiode': '', 'dat_Sitzung': '', 'top': {}}
liste_dict = []
liste_top = []
liste_alle =[]

for item in soup.find_all('strong'):
    print(item.get_text())
    if item.get_text().__contains__('Wahlperiode'):
        dict = {'num_Sitzung': item.get_text()[7:10], 'num_Wahlperiode': item.get_text()[21:23], 'dat_Sitzung': item.get_text()[38:48]}
        liste_dict.append(dict)
    if item.get_text().__contains__('TOP'):
        #print(para.get_text())
        liste_top.append(item.get_text())
    liste_alle.append(item.get_text())

liste_nummern_sitzungsstart = []
liste_nummern_sitzungsende = []
for i, j in enumerate(liste_alle):
    if j == '\n  TOP Sitzungseröffnung ':
        liste_nummern_sitzungsstart.append(i)
for i, j in enumerate(liste_alle):
    if j == '\n  TOP Sitzungsende ':
        liste_nummern_sitzungsende.append(i)
print(liste_nummern_sitzungsstart)
print(liste_nummern_sitzungsende)
eine_Sitzung = []
alle = []
x = 0
start = 0
end = len(liste_nummern_sitzungsende)-1
active = True
while active:
    eine_Sitzung = []
    if start > end:
        active = False
    else:
        eine_Sitzung.append(liste_alle[liste_nummern_sitzungsstart[x]:liste_nummern_sitzungsende[x]])  # [alle zwischen Start:Ende]

        liste_dict[x]['top'] = eine_Sitzung
    x += 1
    start += 1
    alle.append(eine_Sitzung)
# print(len(alle))
# print(eine_Sitzung)
# print(alle)
# print(dict)
# print(liste_dict)
print(liste_dict[0]['top'])

topics = liste_dict[0]['top'][0]
beginn = '\n  TOP Sitzungseröffnung '
lam = 'Lammert, Prof. Dr. Norbert'
topics.remove(beginn)
topics.remove(lam)
topics.index

dict_rede       = {}
dict_sitzung    = {}
list_redner     = []
top_counter     = -1

top_zwischenspeicher = ''

for i in range(len(topics)):

    topic = topics[i]
    topic = topic.strip()
    #print(topic)
    if topic.__contains__('TOP'):
        top_counter = top_counter +1
        list_redner = []
        top_zwischenspeicher = topic
        top_number_key = rebuild_topic(topic, 2)
        top_name = get_topic_name_from_topic_number(top_number_key, topic)
        dict_rede = {top_number_key: top_name}
    else:
        list_redner.append(topic)

    dict_sitzung[top_counter] = {
                    'Sitzung 283':dict_rede,
                    'Redner': list_redner
                }

print(dict_sitzung)
print('test')
