import urllib
from urllib import request
from bs4 import BeautifulSoup

import  lxml
from lxml import etree

bundestag = "http://www.bundestag.de/dokumente/protokolle"

#Query the website and return the html to the variable 'page'
page = urllib.request.urlopen(bundestag)

#Parse the html in the 'page' variable, and store it in Beautiful Soup format
soup = BeautifulSoup(page,"html.parser")
# print(soup.prettify())
# print(soup.title)
# print(soup.a)
tables = soup.find('table', {"class" : 'table bt-table-data'})
#print(tables)
print(tables)
#xpath: /html/body/main/div[4]/div[3]/div/div[1]/div/div/div[1]/table

