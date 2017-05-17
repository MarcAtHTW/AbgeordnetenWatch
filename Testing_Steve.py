import PyPDF2
'''
Data extracting from Plenarprotokoll
'''

txtDir = "C:/PycharmProjects/AbgeordnetenWatch/pdftotxt/"

pdf_file = open('C:\PycharmProjects\AbgeordnetenWatch\Plenarprotokoll_18_232.pdf', 'rb')
read_pdf = PyPDF2.PdfFileReader(pdf_file)
#pages = read_pdf.getPage(0)
#page_content = pages.extractText()
page_content = ''

'''
get content fuer alle Seiten im Protokoll
'''
for i in range(read_pdf.getNumPages()):
    print(i)
    pages = read_pdf.getPage(i)
    page_content = page_content + pages.extractText()
    page_content

'''
- function fuer content-splitt und vorhalten in Liste
- Dabei entfernen von "\n" und "-" aus Listenelemente
- zusätzliche Speicherung in txt-file
'''
def listToTxt(page_content):
    textFilename = txtDir + "Protokoll.txt"
    textFile = open(textFilename, "w")  # make text file
    list = page_content.split(' ')
    print(list)
    for i in range(0, len(list)):
        list_element = list[i]
        print(list_element)
        list_element = list_element.replace("\n", "")
        list_element = list_element.replace("-", "")
        print("item at index", i, ":", list_element)
        textFile.write(list_element+"\n")
    textFile.close
    print(list)


listToTxt(page_content)



