import requests
from HTMLParser import HTMLParser

WIKI_RANDOM_PAGE = 'https://zh.wikipedia.org/wiki/Special:%E9%9A%8F%E6%9C%BA%E9%A1%B5%E9%9D%A2'

class WikiParser(HTMLParser):
    inTitle = False
    inPara = False
    materials = []
    def handle_starttag(self, tag, attrs):
        if tag == 'p':
            self.inPara = True
        elif tag == 'title':
            self.inTitle = True
    def handle_endtag(self, tag):
        if tag == 'p':
            self.inPara = False
        elif tag == 'title':
            self.inTitle = False

    def handle_data(self, data):
        if self.inPara:
            self.materials.append(data)
        elif self.inTitle:
            print 'Parsing: %s' % (data)


if __name__ == '__main__':
    parser = WikiParser()
    for i in range(1000):
        print 'Getting page NO.%d' % (i)
        page = requests.get(WIKI_RANDOM_PAGE)
        parser.feed(page.content.decode('utf-8'))
    f = open('WikiData2.txt', 'w')
    f.write(' '.join(parser.materials).encode('utf-8'))

