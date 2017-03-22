# -*- coding:utf-8 -*-
import math
import logging
import config
# logging.basicConfig(level=logging.INFO)

def getWords(fn):

    f = file(fn, 'r')
    str = f.read().decode('utf-8')
    f.close()
    word2Number = {}
    number2Word = []
    cnt = 0
    for word in str:
        word2Number[word] = cnt
        number2Word.append(word)
        cnt += 1
    return (word2Number, number2Word)

def getPVec(fn):

    f = file(fn, 'r')
    pVec = map(float, f.read().split(' '))
    return pVec


def getPMat(fn):

    f = file(fn, 'r')
    strVec = f.read().split('\n')
    pMat = [map(float, row.split(' ')) for row in strVec]
    return pMat

def getPinyin(fn):

    Pinyin2Word = {}
    f = file(fn, 'r')
    for line in f.readlines():
        lineArr = line.decode('utf-8').strip().split(' ')
        words = []
        pinyin = lineArr[0]
        words = lineArr[1:]
        Pinyin2Word[pinyin] = words
    return Pinyin2Word

def Viterbi(pinyinStr, pVec, pMat, Pinyin2Word, word2Number, number2Vec):

    pinyins = pinyinStr.split(' ')
    P = {}
    paths = {}
    if len(pinyins) is 0:
        return ''
    states = Pinyin2Word[pinyins[0]]
    # logging.info('Start: %s' % (str(states)))
    for state in states:
        P[state] = pVec[word2Number[state]]
        paths[state] = [state]
    for pinyin in pinyins[1:]:
        # logging.info('Consider: %s' % (pinyin))
        newP = {}
        newPaths = {}
        newStates = Pinyin2Word[pinyin]
        # logging.info('Candidates: %s' % (str(newStates)))
        for state in newStates:
            calc = [P[prevState] + pMat[word2Number[prevState]][word2Number[state]] for prevState in states]
            p = -float('inf')
            prevId = 0
            for (index, v) in enumerate(calc):
                if v > p:
                    p = v
                    prevId = index
            prev = states[prevId]
            newP[state] = p
            newPaths[state] = paths[prev][:]
            newPaths[state].append(state)
        P = newP
        paths = newPaths
        states = newStates
    maxPathState = state[0]
    maxP = -float('inf')
    for state in states:
        if P[state] > maxP:
            maxP = P[state]
            maxPathState = state
    return ''.join(paths[maxPathState])


if __name__ == '__main__':

    (word2Number, number2Word) = getWords('WordTable.txt')
    pVec = getPVec(config.VEC_PROB_FILE)
    pMat = getPMat(config.MAT_PROB_FILE)
    Pinyin2Word = getPinyin('Pinyin.txt')

    case = open('TESTCASE.txt', 'r')
    cases = [item.decode('utf-8') for item in case.readlines()]
    cnt = len(cases) / 2
    correct = 0
    for i in range(cnt):
        pinyin = cases[i * 2].strip().lower()
        ans = cases[i * 2 + 1].strip()
        try:
            myans = Viterbi(pinyin, pVec, pMat, Pinyin2Word, word2Number, number2Word)
        except:
            print 'Oops!'
            continue
        if myans == ans:
            correct += 1
        else:
            print 'WRONG ANS!\nAns: %s\nYours: %s' % (ans, myans)
    print 'Tot: %d  Correct: %d  Rate: %f' % (cnt, correct, float(correct) / cnt)
    while True:
        input = raw_input('>> ')
        print Viterbi(input, pVec, pMat, Pinyin2Word, word2Number, number2Word)

