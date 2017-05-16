import PyPDF2

txtDir = "C:/PycharmProjects/AbgeordnetenWatch/pdftotxt/"

pdf_file = open('C:\PycharmProjects\AbgeordnetenWatch\Plenarprotokoll_18_232.pdf', 'rb')
read_pdf = PyPDF2.PdfFileReader(pdf_file)
#pages = read_pdf.getPage(0)
#page_content = pages.extractText()
page_content = ''

for i in range(read_pdf.getNumPages()):
    print(i)
    pages = read_pdf.getPage(i)
    page_content = page_content + pages.extractText()
    page_content.encode("utf-8")

def listToTxt(page_content):
    textFilename = txtDir + "Protokoll.txt"
    textFile = open(textFilename, "w")  # make text file
    list = page_content.split(' ')
    print(list)
    for i in range(0, len(list)):
        list_element = list[i].encode("utf-8")
        print(list_element)
        list_element = list_element.replace("\n", "")
        list_element = list_element.replace("-", "")
        print("item at index", i, ":", list_element)
        textFile.write(list_element+"\n")
    textFile.close
    print(list)


listToTxt(page_content)



