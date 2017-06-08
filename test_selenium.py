from selenium import webdriver
url='C:/Python36-32/BrowserDriver'

browser = webdriver.Firefox(url)
browser.get("http://www.bundestag.de/ajax/filterlist/de/dokumente/protokolle/-/442112/h_6810466be65964217012227c14bad20f?limit=1")

from bs4 import BeautifulSoup

soup=BeautifulSoup(browser.page_source,'lxml')

# for link in soup.find_all('a'):
#     print(link.get('href',None),link.get_text())
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
# print(liste_alle)
# print(liste_dict)
# print(liste_top)

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
        #print("false")
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
zwischen_dict = {}
redner_dict = []
liste_zwischen_dict = []
top_zwischenspeicher = ''
for i in range(len(topics)):
    topic = topics[i]
    topic = topic.strip()
    print(topic)
    if topic.__contains__('TOP'):
        top_zwischenspeicher = topic
        zwischen_dict['Tagesordnungspunkt'] = topic
        liste_zwischen_dict.append(zwischen_dict['Tagesordnungspunkt'])
    else:
        zwischen_dict['Redner'] = redner_dict.append(topic)

print(zwischen_dict)
