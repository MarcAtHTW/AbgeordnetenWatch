rede = []
rede.append('Das ist eine spürbare Verbesserung dessen, (Beifall bei SPD) was die Erwerbsgeminderten an vorzeitiger Rente bekommen – im Schnitt um 7 Prozent.(Beifall bei der SPD und der CDU/CSU)(Widerruf xxxx)')
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
for item in rede:
    clean_rede = rede
    if any(m in item for m in matchers):
        # suche, schneide aus
        liste_treffer = []
        liste_treffer = re.findall(regex, item)
        clean_item = item
        for i in liste_treffer:
            if i.__contains__('Beifall'):
                liste_beifaelle.append(i)
            elif i.__contains__('Widerruf'):
                liste_widersprueche.append(i)
            elif i.__contains__('Unruhe'):
                liste_widersprueche.append(i)
            else:
                liste_wortmeldungen
            clean_item = clean_item.replace('('+i+')', '')
        print(clean_item)
        # clean_rede.append(clean_item)
        # print(liste_beifaelle)
        # print(liste_widersprueche)
        # print(clean_rede)

    else:
        clean_rede.append(item)
print(clean_rede)
