import urllib
from urllib import request

import pandas as pd
from bs4 import BeautifulSoup

bundestag = "http://www.bundestag.de/ajax/filterlist/de/dokumente/protokolle/-/442112/h_6810466be65964217012227c14bad20f?limit=1"

#Query the website and return the html to the variable 'page'
page = urllib.request.urlopen(bundestag)
page = page.read().decode('utf-8')
#Parse the html in the 'page' variable, and store it in Beautiful Soup format

soup = BeautifulSoup(page,"lxml")
table = soup.find('table', {"class" : 'table bt-table-data'})
print(table)

table_rows = table.find_all('tr')
a_tags = table.find_all('a')
for tr in table_rows:
    td = tr.find_all('td')
    row =[i.text for i in td]
    print(row)
    for a in a_tags:
        a = tr.find_all('')
        row = [i.text for i in td]
        print(row)

all_titles = hxs.select('//a')
for titles in all_titles:
    title = titles.select('//title/text()').extract()
    link = titles.select('a/@href').extract()
    print(title)
    print(link)

df = pd.read_html(bundestag)
#print(df.head())


# def parse_url(url):
#     response = urllib.request.urlopen(bundestag)
#     soup = BeautifulSoup(response, 'lxml')
#     return [('table', {"class" : 'table bt-table-data'}, parse_html_table(table))for table in soup.find_all('table')]
#
# def parse_html_table(table):
#     n_columns = 0
#     n_rows = 0
#     column_names = []
#
#     # Find number of rows and columns
#     # we also find the column titles if we can
#     for row in table.find_all('tr'):
#
#         # Determine the number of rows in the table
#         td_tags = row.find_all('td')
#         if len(td_tags) > 0:
#             n_rows += 1
#             if n_columns == 0:
#                 # Set the number of columns for our table
#                 n_columns = len(td_tags)
#
#         # Handle column names if we find them
#         th_tags = row.find_all('th')
#         if len(th_tags) > 0 and len(column_names) == 0:
#             for th in th_tags:
#                 column_names.append(th.get_text())
#
#     # Safeguard on Column Titles
#     if len(column_names) > 0 and len(column_names) != n_columns:
#         raise Exception("Column titles do not match the number of columns")
#
#     columns = column_names if len(column_names) > 0 else range(0, n_columns)
#     df = pd.DataFrame(columns=columns,
#                       index=range(0, n_rows))
#     row_marker = 0
#     for row in table.find_all('tr'):
#         column_marker = 0
#         columns = row.find_all('td')
#         for column in columns:
#             df.iat[row_marker, column_marker] = column.get_text()
#             column_marker += 1
#         if len(columns) > 0:
#             row_marker += 1
#
#     # Convert to float if possible
#     for col in df:
#         try:
#             df[col] = df[col].astype(float)
#         except ValueError:
#             pass
#
#     return df


#print(list(list_table.columns.values))
import pandas as pd

data1 = pd.read_html(page,skiprows=0)[0]
print(data1)
print(list(data1.columns.values))
print(data1.columns.values[0])
