

liste = ['kk Hendricks']
import xlrd

workbook = xlrd.open_workbook('mdb.xls')
worksheet = workbook.sheet_by_name('Tabelle1')
first_col_Names = worksheet.col_values(0)  # Spalte mit Namen, die KEINE Bindestriche enthalten
second_col_Names = worksheet.col_values(1)  # Spalte mit Namen, die Bindestriche enthalten
third_col_Party = worksheet.col_values(2)
print(first_col_Names)
print(second_col_Names)
print(third_col_Party)
matchers = first_col_Names
for i in range(len(liste)):
    list_element = liste[i]
    for m in range(len(matchers)):
        matcher_element = matchers[m]
        if matcher_element.__contains__(list_element) or list_element.__contains__(matcher_element):
            print("listen_eintrag", i, ": ", list_element)
            print("excel_eintrag_name", m, ": ", matcher_element)
            print("excel_eintrag_name_mit_Bindestrich", m, ": ", second_col_Names[m])
            print("excel_eintrag_partei", m, ": ", third_col_Party[m])
            politican_name = second_col_Names[m]
            party_name = third_col_Party[m]

''' Anbindung API-Abgeordnetenwatch - JSON Data-Extract'''
# import urllib.request, json
# politican_name = politican_name.lower()
# print(politican_name)
# politican_name = politican_name.replace(' ','-')
# print(politican_name)
# with urllib.request.urlopen("https://www.abgeordnetenwatch.de/api/profile/"+politican_name+"/profile.json") as url:
#     data = json.loads(url.read().decode())
#     print(data)
#     print(data['profile']['personal']['first_name']+ " " +data['profile']['personal']['last_name'])
#     print(data['profile']['party'])