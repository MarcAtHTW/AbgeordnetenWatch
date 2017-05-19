import PyPDF2
from nltk.corpus import stopwords
'''
    Data extracting from Plenarprotokoll
'''

''' get content fuer alle Seiten im Protokoll '''
def getContent():
    pdf_file = open('C:\PycharmProjects\AbgeordnetenWatch\Plenarprotokoll_18_232.pdf', 'rb')
    read_pdf = PyPDF2.PdfFileReader(pdf_file)
    page_content = ''
    for i in range(read_pdf.getNumPages()):
        print(i)
        pages = read_pdf.getPage(i)
        page_content += pages.extractText()
    return page_content
'''
- function fuer content-splitt und vorhalten in Liste
- Dabei entfernen von "\n" und "-" aus Listenelemente
- zusätzliche Speicherung in txt-file
'''
def listToTxt(page_content):
    txtDir = "C:/PycharmProjects/AbgeordnetenWatch/pdftotxt/"
    textFilename = txtDir + "Protokoll.txt"
    textFile = open(textFilename, "w")  # make text file
    list = page_content.split(' ')
    print(list)
    cleanList = []
    for i in range(len(list)):
        list_element = list[i]
        list_element = list_element.replace("\n", "")
        list_element = list_element.replace("-", "")
        cleanList.append(list_element) # liste ohne -, \n
        #print("item at index", i, ":", list_element)
        #textFile.write(list_element+"\n")
    return cleanList

''' stop_words aus liste entfernen'''
def filteredSentence(wordlist):
    #set stop words
    stop_words = set(stopwords.words("german"))
    print(stop_words)
    filtered_sentence = [w for w in wordlist if not w in stop_words]
    print(filtered_sentence)
    return filtered_sentence


#start with an empty list
dl_protocol = []

# make a new dic for datarow and add them to the list
datarow = {'tag':'',
       'top':'',
       'thema':'',
       'politiker': '',
       'partei': '',
       'redetext':''
       }
dl_protocol.append(datarow)
print(dl_protocol)
# Show all information about each datarow.
for datarows in dl_protocol:
    for k, v in datarow.items():
        print(k + ": " + v)
    print("\n")

# neues dic für jeden neuen Datensatz

datarow['tag']


content = getContent()
wordlist = listToTxt(content)
filteredSentence(wordlist)





