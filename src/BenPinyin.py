# -*- coding:utf-8 -*-
import math
import config
import getopt
import sys

class Vocabulary:
    hanzi2Idx = {}
    idx2Hanzi = []
    pinyin2Hanzi = {}
    pinyin2Idx = {}
    def __init__(self, hanziListFile, pinyin2HanziFile):
        f = open(hanziListFile, 'r')
        hanziStr = f.read().decode('utf-8')
        f.close()
        cnt = 0
        for hanzi in hanziStr:
            self.hanzi2Idx[hanzi] = cnt
            self.idx2Hanzi.append(hanzi)
            cnt += 1
        f = open(pinyin2HanziFile, 'r')
        for line in f.readlines():
            lineArr = line.decode('utf-8').strip().split(' ')
            pinyin = lineArr[0]
            hanziList = lineArr[1:]
            self.pinyin2Hanzi[pinyin] = hanziList
            idxList = [self.hanzi2Idx[hanzi] for hanzi in hanziList]
            self.pinyin2Idx[pinyin] = idxList
        f.close()
    def decode(self, idxList):
        return [self.idx2Hanzi[idx] for idx in idxList]
    def fromPinyin(self, pinyinList):
        return [[self.hanzi2Idx[hanzi] for hanzi in self.pinyin2Hanzi[pinyin]] for pinyin in pinyinList]
    def getHanziIdx(self, hanzi):
        return self.hanzi2Idx[hanzi]

class Vocabulary3(Vocabulary):
    gram2Idx = {}
    idx2Gram = []
    def __init__(self, hanziListFile, gramListFile, pinyin2HanziFile):
        Vocabulary.__init__(self, hanziListFile, pinyin2HanziFile)
        f = open(gramListFile, 'r')
        self.idx2Gram = f.read().decode('utf-8').split(' ')
        f.close()
        for idx, gram in enumerate(self.idx2Gram):
            self.gram2Idx[gram] = idx
    def hasGram(self, gram):
        return self.gram2Idx.has_key(gram)
    def getGramIdxFromHanziIdx(self, i1, i2):
        hanzi1 = self.idx2Hanzi[i1]
        hanzi2 = self.idx2Hanzi[i2]
        gram = hanzi1 + hanzi2
        if self.gram2Idx.has_key(gram):
            return self.gram2Idx[gram]
        else:
            return -1

class PinyinSplitter:
    def __init__(self):
        pass
    def split(self, pinyin):
        return pinyin.split(' ')

class PinyinTranslator:
    def __init__(self, hanziListFile, pinyin2HanziFile, vecFile, matFile):
        self.__splitter = PinyinSplitter()
        self.__vocabulary = Vocabulary(hanziListFile, pinyin2HanziFile)
        self.__pMat = self.__getMatFromFile(matFile)
        self.__pVec = self.__getVecFromFile(vecFile)
    def __getVecFromFile(self, vecFile):
        f = open(vecFile, 'r')
        pVec = map(float, f.read().split(' '))
        f.close()
        return pVec
    def __getMatFromFile(self, matFile):
        f = file(matFile, 'r')
        strVec = f.read().split('\n')
        pMat = [map(float, row.split(' ')) for row in strVec]
        f.close()
        return pMat
    def translate(self, pinyinStr):
        pinyinList = self.__splitter.split(pinyinStr)
        hanziIdxList = self.__vocabulary.fromPinyin(pinyinList)
        path = [[0 for i in range(0, len(list))] for list in hanziIdxList]
        P = []
        for idx in hanziIdxList[0]:
            P.append(self.__pVec[idx])
        for i in range(1, len(hanziIdxList)):
            newP = []
            for index, hanzi in enumerate(hanziIdxList[i]):
                maxP = - float('inf')
                maxI = 0
                for indexPrev, prev in enumerate(hanziIdxList[i - 1]):
                    currentP = self.__pMat[prev][hanzi] + P[indexPrev]
                    if currentP > maxP:
                        maxP = currentP
                        maxI = indexPrev
                newP.append(maxP)
                path[i][index] = maxI
            P = newP
        bestPath = []
        bestP = - float('inf')
        currentVisit = 0
        for i, p in enumerate(P):
            if p > bestP:
                bestP = p
                currentVisit = i
        bestPath.append(hanziIdxList[-1][currentVisit])
        for i in range(len(hanziIdxList) - 1, 0, -1):
            currentVisit = path[i][currentVisit]
            bestPath.append(hanziIdxList[i - 1][currentVisit])
        translated = self.__vocabulary.decode(bestPath[::-1])
        return ''.join(translated)

class PinyinTranslator3:
    def __init__(self, hanziListFile, gramListFile, pinyin2HanziFile, vecFile, vecFile3, matFile3):
        self.__splitter = PinyinSplitter()
        self.__vocabulary3 = Vocabulary3(hanziListFile, gramListFile, pinyin2HanziFile)
        self.__fMat = self.__getMatFromFile(matFile3)
        self.__hanziVec = self.__getVecFromFile(vecFile, float)
        self.__fVec = self.__getVecFromFile(vecFile3, int)
        self.__fVecSum = sum(self.__fVec)
    def __getVecFromFile(self, vecFile, type):
        f = open(vecFile, 'r')
        fVec = map(type, f.read().split(' '))
        f.close()
        return fVec
    def __getMatFromFile(self, matFile):
        fMat = {}
        f = file(matFile, 'r')
        strVec = f.read().split('\n')
        f.close()
        for paramStr in strVec:
            params = map(int, paramStr.split(' '))
            if not fMat.has_key(params[0]):
                fMat[params[0]] = {params[1]: params[2]}
            else:
                fMat[params[0]][params[1]] = params[2]
        return fMat
    def __getTriGramP(self, i1, i2, i3):
        gramIdx = self.__vocabulary3.getGramIdxFromHanziIdx(i1, i2)
        hanziIdx = i3
        if gramIdx is -1:
            return math.log(float(1) / config.N_HANZI)
        else:
            if self.__fMat[gramIdx].has_key(hanziIdx):
                return math.log(float(1 + self.__fMat[gramIdx][hanziIdx]) / (self.__fVec[gramIdx] + config.N_HANZI))
            else:
                return math.log(float(1) / (self.__fVec[gramIdx] + config.N_HANZI))
    def __getGramP(self, i1, i2):
        pass
    def translate(self, pinyinStr):
        pinyinList = self.__splitter.split(pinyinStr)
        pinyinCnt = len(pinyinList)
        hanziIdxList = self.__vocabulary3.fromPinyin(pinyinList)
        if pinyinCnt is 1:
            maxP = - float('inf')
            bestHanzi = 0
            for hanziIdx in hanziIdxList[0]:
                p = self.__hanziVec[hanziIdx]
                if p > maxP:
                    maxP = p
                    bestHanzi = hanziIdx
            return ''.join(self.__vocabulary3.decode([bestHanzi]))

        path = []
        P = []
        path.append([])
        P.append([])
        for i in range(1, pinyinCnt):
            path.append([[0 for k in range(0, len(hanziIdxList[i - 1]))]for j in range(0, len(hanziIdxList[i]))])
            P.append([[0 for k in range(0, len(hanziIdxList[i - 1]))] for j in range(0, len(hanziIdxList[i]))])
        for i in range(0, len(hanziIdxList[1])):
            for j in range(0, len(hanziIdxList[0])):
                gramIdx = self.__vocabulary3.getGramIdxFromHanziIdx(hanziIdxList[0][j], hanziIdxList[1][i])
                P[1][i][j] = - float('inf') if gramIdx is -1 else math.log(float(self.__fVec[gramIdx]) / self.__fVecSum)
        for i in range(2, pinyinCnt):
            for j in range(0, len(hanziIdxList[i])):
                for k in range(0, len(hanziIdxList[i - 1])):
                    maxPrePrev = 0
                    maxP = - float('inf')
                    for p in range(0, len(hanziIdxList[i - 2])):
                        currentP = P[i - 1][k][p] + self.__getTriGramP(hanziIdxList[i - 2][p], hanziIdxList[i - 1][k], hanziIdxList[i][j])
                        if currentP > maxP:
                            maxP = currentP
                            maxPrePrev = p
                    P[i][j][k] = maxP
                    path[i][j][k] = maxPrePrev
        maxP = - float('inf')
        bestJ = bestK = 0
        for j in range(0, len(hanziIdxList[pinyinCnt - 1])):
            for k in range(0, len(hanziIdxList[pinyinCnt - 2])):
                currentP = P[pinyinCnt - 1][j][k]
                if currentP > maxP:
                    maxP = currentP
                    bestJ = j
                    bestK = k
        bestPath = []
        bestPath.append(hanziIdxList[pinyinCnt - 1][bestJ])
        bestPath.append(hanziIdxList[pinyinCnt - 2][bestK])
        for i in range(0, pinyinCnt - 2):
            bestPrePrev = path[pinyinCnt - 1 - i][bestJ][bestK]
            bestPath.append(hanziIdxList[pinyinCnt - 3 - i][bestPrePrev])
            bestJ = bestK
            bestK = bestPrePrev
        translated = self.__vocabulary3.decode(bestPath[::-1])
        return ''.join(translated)


class BenPinyin:
    __translator = None
    def __init__(self, ngram = 2):
        if ngram is 2:
            print 'Loading data ... It\'ll take about 30 seconds.'
            self.__translator = PinyinTranslator(config.HANZI_LIST_FILE, config.PINYIN_FILE, config.VEC_DATA_FILE, config.MAT_DATA_FILE)
        elif ngram is 3:
            print 'Loading data ... It\'ll take about 2 minutes.'
            self.__translator = PinyinTranslator3(config.HANZI_LIST_FILE, config.GRAM_LIST_FILE_3, config.PINYIN_FILE, config.VEC_DATA_FILE, config.VEC_DATA_FILE_3, config.MAT_DATA_FILE_3)
    def shell(self):
        print 'Welcome to BenPinyin shell!'
        while True:
            input = raw_input('>>> ')
            if input == 'exit':
                sys.exit()
            try:
                print self.__translator.translate(input.strip().lower())
            except:
                print 'Oops, something\'s wrong!'
    def fileIO(self, inFile, outFile):
        fin = open(inFile, 'r')
        fout = open(outFile, 'w')
        cnt = 0
        for line in fin.readlines():
            try:
                fout.write(self.__translator.translate(line.strip().lower()).encode('utf-8'))
                fout.write('\n')
                cnt += 1
            except:
                print 'Oops, something\'s wrong!'
        fin.close()
        fout.close()
        print '%d sentences successfully translated.' % (cnt)
    def test(self, testFile):
        case = open(testFile, 'r')
        cases = case.read().decode('utf-8').split('\n')
        case.close()
        caseCnt = len(cases) / 2
        hanziCnt = 0
        correctHanzi = 0
        correctCase = 0
        failCase = 0
        errorCase = 0
        for i in range(caseCnt):
            pinyin = cases[i * 2].strip().lower()
            ans = cases[i * 2 + 1].strip()
            try:
                myAns = self.__translator.translate(pinyin)
            except:
                print 'Oops, something\'s wrong!'
                failCase += 1
                continue
            if len(myAns) is not len(ans):
                print 'Pinyin length and answer length not match!'
                failCase += 1
                continue
            hanziCnt += len(ans)
            for i, hanzi in enumerate(ans):
                if hanzi == myAns[i]:
                    correctHanzi += 1
            if myAns == ans:
                correctCase += 1
            else:
                print 'Wrong answer! \nCorrect answer: %s\nYour answer: %s\n-------------' % (ans, myAns)
                errorCase += 1
        print 'Total case: %d' % (caseCnt)
        print 'Sentence accuracy: %f' % (float(correctCase) / (caseCnt - failCase))
        print 'Hanzi accuracy: %f' % (float(correctHanzi) / hanziCnt)


if __name__ == '__main__':

    try:
        opts, args = getopt.getopt(sys.argv[1:], "t:i:o:", ['ngram='])
    except getopt.GetoptError:
        print 'Command not found.'
        sys.exit()
    haveI = False
    haveO = False
    haveT = False
    inFile = ''
    outFile = ''
    testFile = ''
    N_GRAM = 2
    for o, a in opts:
        if o in ['-i']:
            haveI = True
            inFile = a
        elif o in ['-o']:
            haveO = True
            outFile = a
        elif o in ['-t']:
            haveT = True
            testFile = a
        elif o in ['--ngram']:
            try:
                N_GRAM = int(a)
            except:
                print 'N-GRAM param not valid.'
                sys.exit()
    haveIO = haveI and haveO
    Ben = BenPinyin(N_GRAM)
    if haveIO and (not haveT):
        Ben.fileIO(inFile, outFile)
        sys.exit()
    elif haveT and (not haveIO):
        Ben.test(testFile)
        sys.exit()
    elif (not haveT) and (not haveIO):
        Ben.shell()
        sys.exit()
    else:
        print 'Command not found.'
        sys.exit()



