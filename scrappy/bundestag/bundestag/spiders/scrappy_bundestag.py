import scrapy
import urllib


#from urllib import request
#from bs4 import BeautifulSoup
from scrapy.cmdline import execute
#from scrapy.selector import HtmlXPathSelector
from scrapy import Selector

class QuotesSpider(scrapy.Spider):
    name = "bundestag"

    def start_requests(self):
        urls = [
            #'http://www.bundestag.de/ajax/filterlist/de/dokumente/protokolle/-/442098/h_88d94992de906f1bc6e2fd6b559d49d5?limit=10&noFilterSet=true&noPagination=true&offset=0'
            #'http://www.bundestag.de/dokumente/protokolle'
            #'http://www.bundestag.de/static/appdata/filter/sitzungen.json'
            'http://www.bundestag.de/ajax/filterlist/de/dokumente/protokolle/-/442112/h_6810466be65964217012227c14bad20f?limit=10&noFilterSet=true'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = '../../bundestag-%s.html' % page
        response_html = response.body

        #hxs = HtmlXPathSelector(response)
        hxs = Selector(response)
        '''
        body = response.body
        titles = hxs.xpath('//title/text()')
        final = titles.extract()
        print(final)
        '''

        all_titles = hxs.select('//a')
        for titles in all_titles:
            title = titles.select('//title/text()').extract()
            link = titles.select('a/@href').extract()
            print(title)
            print(link)


        '''
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)        
        '''


execute(['scrapy','crawl','bundestag'])
#page = urllib.request.urlopen('http://www.bundestag.de/ajax/filterlist/de/dokumente/protokolle/-/442112/h_6810466be65964217012227c14bad20f?limit=1')
#soup = BeautifulSoup(page, 'lxml')
#print(soup.prettify())
