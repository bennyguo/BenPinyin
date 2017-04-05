# -*- coding:utf-8 -*-
import requests
from HTMLParser import HTMLParser
import threading
import Queue
import jieba
# WIKI_RANDOM_PAGE = 'https://zh.wikipedia.org/wiki/Special:%E9%9A%8F%E6%9C%BA%E9%A1%B5%E9%9D%A2'
urlList = None
urlListMutex = threading.Lock()
fileMutex = threading.Lock()
queue = Queue.Queue()

def unicodeToUrlParam(ustr):
    urlParam = ''
    for hanzi in ustr:
        utfArr = [c for c in hanzi.encode('utf-8')]
        paramStr = ''.join(['%' + hex(ord(c))[2:] for c in utfArr])
        urlParam += paramStr
    return urlParam

def getHanziUrlList(fn):
    f = open(fn, 'r')
    hanziArr = [c for c in f.read().decode('utf-8')]
    urlList = []
    for hanzi in hanziArr:
        url = 'http://baike.baidu.com/item/' + unicodeToUrlParam(hanzi)
        urlList.append(url)
    return urlList


def getTestCaseWordUrlList(fn):
    sentenceList = []
    f = open(fn, 'r')
    for idx, line in enumerate(f.readlines()):
        if idx % 2 is 1:
            sentenceList.append(line)
    wordList = []
    for sentence in sentenceList:
        wordList += [word for word in list(jieba.cut(sentence, cut_all=True)) if len(word) > 1]
    urlList = []
    for word in wordList:
        urlList.append('http://baike.baidu.com/item/' + unicodeToUrlParam(word))
    return urlList

def getTestCasePolysemantUrlList(wordUrlList, fn = 'BaiduBaikeWord/urls.txt'):
    parser = BaikePolysemantParser()
    urlList = []
    for idx, url in enumerate(wordUrlList):
        print 'Parsing original url NO.%d' % (idx)
        page = requests.get(url).content.decode('utf-8')
        parser.feed(page)
        if len(parser.urlList) is 0:
            urlList.append(url)
        else:
            urlList += parser.urlList
            parser.urlList = []
    f = open(fn, 'a')
    f.write('\n'.join(urlList))
    f.close()
    print 'Parsing finished.'
    print 'Original: %d pages, Parsed: %d pages.' % (len(wordUrlList), len(urlList))



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

class BaikePolysemantParser(HTMLParser):
    inLi = False
    urlList = []
    def handle_starttag(self, tag, attrs):
        if tag == 'li':
            for key, value in attrs:
                if key == 'class' and value == 'item':
                    self.inLi = True
        elif self.inLi and tag == 'a':
            for key, value in attrs:
                if key == 'href':
                    self.urlList.append('http://baike.baidu.com' + value)
    def handle_endtag(self, tag):
        if tag == 'li':
            self.inLi = False

class BaikeParser(HTMLParser):
    inTitle = False
    inPara = False
    materials = []
    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            for key, value in attrs:
                if key == 'class' and value == 'para':
                    self.inPara = True
        elif tag == 'title':
            self.inTitle = True
    def handle_endtag(self, tag):
        if tag == 'div':
            self.inPara = False
        elif tag == 'title':
            self.inTitle = False

    def handle_data(self, data):
        if self.inPara:
            self.materials.append(data.strip())
        elif self.inTitle:
            print 'Parsing: %s' % (data)

class MyThread(threading.Thread) :
    def __init__(self, fn):
        threading.Thread.__init__(self)
        self.parser = BaikeParser()
        self.fn = fn
    def run(self):
        while True:
            if queue.empty():
                break
            currentUrl = queue.get()
            page = requests.get(currentUrl).content.decode('utf-8')
            self.parser.feed(page)
            f = open(self.fn, 'a')
            f.write(' '.join(self.parser.materials).encode('utf-8'))
            f.close()
            self.parser.materials = []
            queue.task_done()
        print 'Thread %s exit.' % (self.fn)

def BaikeHanziSpider():
    urlList = getHanziUrlList('WordTable.txt')
    for url in urlList:
        queue.put(url)
    threads = []
    nThreads = 6
    for i in range(nThreads):
        threads.append(MyThread('BaiduBaikeHanzi/BaikeData%d.txt' % (i)))
    for thread in threads:
        thread.setDaemon(True)
        thread.start()
    for thread in threads:
        thread.join()
    print 'Done.'

def BaikeWordSpider():
    # After getting all the urls in file
    f = open('BaiduBaikeWord/urls.txt', 'r')
    urls = f.read().split('\n')
    f.close()
    for url in urls:
        queue.put(url)
    threads = []
    nThreads = 8
    for i in range(nThreads):
        threads.append(MyThread('BaiduBaikeWord/BaikeData%d.txt' % (i)))
    for thread in threads:
        thread.setDaemon(True)
        thread.start()
    for thread in threads:
        thread.join()
    print 'Done.'

def mergeFiles(files, fn, sep = '\n'):
    merged = open(fn, 'w')
    for file in files:
        f = open(file, 'r')
        merged.write(f.read())
        merged.write(sep)
        f.close()
    merged.close()


if __name__ == '__main__':
    # getTestCasePolysemantUrlList(getTestCaseWordUrlList('TESTCASE.txt'))
    # base1 = 'BaiduBaikeHanzi/'
    # base2 = 'BaiduBaikeWord/'
    # files1 = []
    # files2 = []
    # for i in range(6):
    #     files1.append(base1 + 'BaikeData%d.txt' % (i))
    # for i in range(8):
    #     files2.append(base2 + 'BaikeData%d.txt' % (i))
    # mergeFiles(files1, base1 + 'merged.txt')
    # mergeFiles(files2, base2 + 'merged.txt')
    files = ['Wikipedia/wiki_00', 'Wikipedia/wiki_01']
    mergeFiles(files, 'Wikipedia/WikiData.txt', sep='\n')

