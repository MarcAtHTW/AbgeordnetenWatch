import xlrd
from datetime import datetime
import xlsxwriter


def create_protocol_workbook():
    # Create a workbook and add a worksheet.
    workbook = xlsxwriter.Workbook('bundestag_protokolle.xlsx')
    worksheet = workbook.add_worksheet()

    # Add a bold format to use to highlight cells.
    bold = workbook.add_format({'bold': 1})

    # Adjust the column width.
    worksheet.set_column(1, 1, 15)

    # Write data headers.
    worksheet.write('A1', 'Sitzungsnummer', bold)
    worksheet.write('B1', 'Sitzungsdatum', bold)
    worksheet.write('C1', 'Wahlperiode', bold)
    worksheet.write('D1', 'Tagesordnungspunkt', bold)
    worksheet.write('E1', 'Tagesordnungspunktbezeichnung', bold)
    worksheet.write('F1', 'Redner', bold)
    worksheet.write('G1', 'Rede', bold)

    worksheet.write('H1', 'beifaelle', bold)
    worksheet.write('I1', 'anzahl_beifaelle', bold)
    worksheet.write('J1', 'wortmeldungen', bold)
    worksheet.write('K1', 'anzahl_wortmeldungen', bold)

    # data we want to write to the worksheet.
    data = (
         [238, '20.06.2017', 18],
         [237, '20.06.2017', 18],
         [236, '20.06.2017', 18],
         [235, '20.06.2017', 18],
         [234, '20.06.2017', 18],
         [233, '20.06.2017', 18],
         [232, '20.06.2017', 18],
         [231, '20.06.2017', 18],
         [230, '20.06.2017', 18],
         [229, '20.06.2017', 18],

     )
    # Start from the first cell below the headers.
    row = 1
    col = 0
    for sitzungsnummer, date_sitzung, nr_wahlperiode in (data):
         worksheet.write_number(row, col, sitzungsnummer)
         worksheet.write_string(row, col +1, date_sitzung)
         worksheet.write_number(row, col +2, nr_wahlperiode)
         #worksheet.write_number(row, col,)
         row += 1


    workbook.close()

create_protocol_workbook()

''' Abgleich mit Excelcheet'''
# def get_data_in_csv(namesOfEntities):
#     temp_dict_entity_polname_partyname = {'polName': '', 'partyName': ''}
#     politican_name = ''
#     party_name = ''
#     workbook = xlrd.open_workbook('mdb.xls')
#     worksheet = workbook.sheet_by_name('Tabelle1')
#     first_col_Names = worksheet.col_values(0)  # Spalte mit Namen, die KEINE Bindestriche enthalten
#     second_col_Names = worksheet.col_values(1)  # Spalte mit Namen, die Bindestriche enthalten
#     third_col_Party = worksheet.col_values(2)
#     matchers = first_col_Names
#     for i in range(len(namesOfEntities)):
#         name = namesOfEntities[i]
#         for m in range(len(matchers)):
#             matcher_element = matchers[m]
#             if matcher_element.__contains__(name) or name.__contains__(matcher_element):
#                 print("listen_eintrag", i, ": ", name)
#                 print("excel_eintrag_name", m, ": ", matcher_element)
#                 print("excel_eintrag_name_mit_Bindestrich", m, ": ", second_col_Names[m])
#                 print("excel_eintrag_partei", m, ": ", third_col_Party[m])
#                 politican_name = second_col_Names[m]
#                 party_name = third_col_Party[m]
#                 temp_dict_entity_polname_partyname = {'polName': politican_name, 'partyName': party_name}
#                 print('wwwwwwwwwwwwwwwwwwwwwwww: ',temp_dict_entity_polname_partyname['polName'])
#                 print('wwwwwwwwwwwwwwwwwwwwwwww: ',temp_dict_entity_polname_partyname['partyName'])
#
#                 ''' Eintrag in DB Name + Partei'''
#
#     return temp_dict_entity_polname_partyname

