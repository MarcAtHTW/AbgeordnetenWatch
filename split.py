rede = []
rede.append('Das ist eine spürbare Verbesserung dessen, (Beifall bei SPD) was die Erwerbsgeminderten an vorzeitiger Rente bekommen – im Schnitt um 7 Prozent.(Beifall bei der SPD und der CDU/CSU)(Widerruf xxxx)')
rede.append('(Wortmeldung ooooo!')
rede.append('(Wortmeldung ooooo)')
rede.append('xxxxxxxxxxxxxxx')


liste_beifaelle = []
liste_widersprueche = []
liste_unruhe = []
liste_wortmeldungen = []
matchers = ['Beifall', 'Widerspruch', 'Unruhe', 'Wortmeldung']
import re

x = 0
# gehe jede Rede durch
# wenn (...) kommt dann entferne diesen Teil aus Rede
# entfernten Teil analysieren und zwischen speichern

regex = re.compile(".*?\((.*?)\)")
char1 = '('
char2 = '!'
clean_rede = []
temp_liste_treffer = []
for item in rede:
    if any(m in item for m in matchers):
        # suche, schneide aus
        liste_treffer = []
        liste_treffer = re.findall(regex, item)
        temp_liste_treffer.append(liste_treffer)
        print('temp_liste_treffer: ', temp_liste_treffer)
        if item.__contains__(char1) and item.__contains__(char2):
            item_between_chars = item[item.find(char1) + 1:item.find(char2)]
            for x in temp_liste_treffer:
                if any(item_between_chars in s for s in x):
                    liste_treffer.append(item_between_chars)
                else:
                    pass

        clean_item = item
        for i in liste_treffer:
            if i.__contains__('Beifall'):
                liste_beifaelle.append(i)
            elif i.__contains__('Widerruf'):
                liste_widersprueche.append(i)
            elif i.__contains__('Unruhe'):
                liste_unruhe.append(i)
            else:
                liste_wortmeldungen.append(i)
            clean_item = clean_item.replace('('+i+')', '')
            clean_item = clean_item.replace('('+i+'!', '')
        clean_rede.append(clean_item)
    else:
        clean_rede.append(item)
print('3: ',liste_beifaelle)
print('4: ',liste_widersprueche)
print('5: ',liste_wortmeldungen)
print('6: ',clean_rede)
