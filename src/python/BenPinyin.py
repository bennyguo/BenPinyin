# -*- coding:utf-8 -*-
import math
import config

class Vocabulary:
    __hanzi2Idx = {}
    __idx2Hanzi = []
    __pinyin2Hanzi = {}
    __pinyin2Idx = {}
    def __init__(self, hanziListFile, pinyin2HanziFile):
        f = open(hanziListFile, 'r')
        hanziStr = f.read().decode('utf-8')
        f.close()
        cnt = 0
        for hanzi in hanziStr:
            self.__hanzi2Idx[hanzi] = cnt
            self.__idx2Hanzi.append(hanzi)
            cnt += 1
        f = open(pinyin2HanziFile, 'r')
        for line in f.readlines():
            lineArr = line.decode('utf-8').strip().split(' ')
            pinyin = lineArr[0]
            hanziList = lineArr[1:]
            self.__pinyin2Hanzi[pinyin] = hanziList
            idxList = [self.__hanzi2Idx[hanzi] for hanzi in hanziList]
            self.__pinyin2Idx[pinyin] = idxList
        f.close()
    def decode(self, idxList):
        return [self.__idx2Hanzi[idx] for idx in idxList]
    def fromPinyin(self, pinyinList):
        return [[self.__hanzi2Idx[hanzi] for hanzi in self.__pinyin2Hanzi[pinyin]] for pinyin in pinyinList]

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


class BenPinyin:
    def __init__(self, hanziListFile, pinyin2HanziFile, vecFile, matFile):
        self.__translator = PinyinTranslator(hanziListFile, pinyin2HanziFile, vecFile, matFile)
    def shell(self):
        pass
    def fileIO(self):
        pass
    def test(self, pinyinStr):
        print self.__translator.translate(pinyinStr)


if __name__ == '__main__':

    ben = BenPinyin(config.HANZI_LIST_FILE, config.PINYIN_FILE, config.VEC_DATA_FILE, config.MAT_DATA_FILE)
    ben.test('qing hua da xue ji suan ji xi')
