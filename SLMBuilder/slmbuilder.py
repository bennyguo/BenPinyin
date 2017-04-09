# -*- coding:utf-8 -*-
import json
from multiprocessing import Pool
import time
import config
import logging
import os
import math
import getopt
import sys
import unicodedata
logging.basicConfig(level=logging.INFO)

def getTime(seconds):
    iseconds = int(seconds)
    hour = iseconds / 3600
    minute = (iseconds % 3600) / 60
    second = iseconds % 60
    return (hour, minute, second)

def getVecFromFile(fn, type, sep = ' '):
    f = open(fn, 'r')
    vec = map(type, f.read().split(sep))
    f.close()
    return vec

def getMatFromFile(fn, type, sepr = '\n', sepc = ' '):
    f = open(fn, 'r')
    strVec = f.read().split(sepr)
    mat = [map(type, row.split(sepc)) for row in strVec]
    f.close()
    return mat

def writeVecToFile(vec, fn):
    f = open(fn, 'w')
    f.write(' '.join(map(str, vec)))
    f.close()

def writeMatToFile(mat, fn):
    f = open(fn, 'w')
    strVec = [' '.join(map(str, row)) for row in mat]
    f.write('\n'.join(strVec))
    f.close()

def writeSparseMatToFile(mat, fn, ignore = 0):
    strVec = []
    nrow = len(mat)
    ncol = len(mat[0])
    for rowIdx, row in enumerate(mat):
        for colIdx, item in enumerate(row):
            if item != ignore:
                strVec.append('%d %d %s' % (rowIdx, colIdx, str(item)))
    f = open(fn, 'w')
    f.write('%d %d\n' % (nrow, ncol))
    f.write('\n'.join(strVec))
    f.close()

def getSparseMatFromFile(fn, type, ignore = 0, sepr = '\n', sepc = ' '):
    f = open(fn, 'r')
    strVec = f.read().split(sepr)
    f.close()
    (nrow, ncol) = map(int, strVec[0].split(sepc))
    mat = [[ignore for i in range(ncol)] for i in range(nrow)]
    for info in strVec[1:]:
        infoArr = info.split(sepc)
        (rowIdx, colIdx, value) = (int(infoArr[0]), int(infoArr[1]), type(infoArr[2]))
        mat[rowIdx][colIdx] = value
    return mat

def addToSparseMatFromFile(fn, mat, type, sepr = '\n', sepc = ' '):
    f = open(fn, 'r')
    strVec = f.read().split(sepr)
    f.close()
    for info in strVec[1:]:
        infoArr = info.split(sepc)
        (rowIdx, colIdx, value) = (int(infoArr[0]), int(infoArr[1]), type(infoArr[2]))
        mat[rowIdx][colIdx] += value

def transferToSparseMatFile(fold, fnew, type, ignore = 0):
    mat = getMatFromFile(fold, type)
    writeSparseMatToFile(mat, fnew, ignore)

def getHanziMapping(fn):
    f = file(fn, 'r')
    str = f.read().decode('utf-8')
    f.close()
    hanzi2Idx = {}
    idx2Hanzi = []
    for (idx, hanzi) in enumerate(str):
        hanzi2Idx[hanzi] = idx
        idx2Hanzi.append(hanzi)
    return (hanzi2Idx, idx2Hanzi)


def getFreqData(text, freqVec, freqMat, word2Number, number2Word):
    textLength = len(text)
    for i in range(1, textLength):
        if not (word2Number.has_key(text[i - 1]) and word2Number.has_key(text[i])):
            continue
        currentIdx = word2Number[text[i]]
        prevIdx = word2Number[text[i - 1]]
        freqMat[prevIdx][currentIdx] += 1
        freqVec[prevIdx] += 1

def mergeVecData(files):
    freqVec = [0 for i in range(config.N_HANZI)]
    for (idx, file) in enumerate(files):
        logging.info('Merging vec freq file NO.%d ...' % (idx))
        f = open(file, 'r')
        vec = map(int, f.read().split(' '))
        if idx is 0:
            freqVec = [0 for i in range(len(vec))]
        for (wordId, freq) in enumerate(vec):
            freqVec[wordId] += freq
        f.close()
    return freqVec

def mergeMatData(files):
    freqMat = [[0 for i in range(config.N_HANZI)] for i in range(config.N_HANZI)]
    for (idx, file) in enumerate(files):
        logging.info('Merging mat freq file NO.%d ...' % (idx))
        addToSparseMatFromFile(file, freqMat, int)
    return freqMat

def processVec(vec, func = math.log, precision = 4):
    tot = float(sum(vec)) + len(vec)
    newVec = [round(func((item + 1) / tot), precision) for item in vec]
    return newVec

def processMat(mat, func = math.log, precision = 4):
    newMat = []
    for (rowIdx, row) in enumerate(mat):
        newMat.append(processVec(row, func, precision))
    return newMat

def build():
    tstart = time.time()
    logging.info('Getting Hanzi from file ...')
    hanzi2Idx, idx2Hanzi = getHanziMapping(config.HANZI_LIST_FILE)
    files = config.DATA_FILE_BASE
    nHanzi = config.N_HANZI
    freqVec = [0 for i in range(nHanzi)]
    freqMat = [[0 for i in range(nHanzi)] for i in range(nHanzi)]
    for file in files:
        logging.info('Start processing file: %s ...' % (file))
        f = open(file, 'r')
        text = f.read().decode('utf-8')
        f.close()
        getFreqData(text, freqVec, freqMat, hanzi2Idx, idx2Hanzi)
    logging.info('Starting prob calculation procedure ...')
    processedVec = processVec(freqVec)
    processedMat = processMat(freqMat)
    logging.info('Starting writing to files ...')
    writeVecToFile(freqVec, config.VEC_FREQ_FILE)
    writeSparseMatToFile(freqMat, config.MAT_FREQ_FILE)
    writeVecToFile(processedVec, config.VEC_PROB_FILE)
    writeMatToFile(processedMat, config.MAT_PROB_FILE)
    (hour, minute, second) = getTime(time.time() - tstart)
    logging.info('Build 2-gram SLM Model finished in %dh%dmin%ds.' % (hour, minute, second))

def addData(fn):
    tstart = time.time()
    logging.info('Getting Hanzi from file ...')
    hanzi2Idx, idx2Hanzi = getHanziMapping(config.HANZI_LIST_FILE)
    logging.info('Reading language material ...')
    f = open(fn, 'r')
    text = f.read().decode('utf-8')
    f.close()
    logging.info('Getting original vec freq file ...')
    freqVec = getVecFromFile(config.VEC_FREQ_FILE, type = int)
    logging.info('Getting original mat freq file ...')
    freqMat = getSparseMatFromFile(config.MAT_FREQ_FILE, type = int)
    logging.info('Append data from new material ...')
    getFreqData(text, freqVec, freqMat, hanzi2Idx, idx2Hanzi)
    logging.info('Writing new freq files ...')
    writeVecToFile(freqVec, config.VEC_FREQ_FILE)
    writeSparseMatToFile(freqMat, config.MAT_FREQ_FILE)
    logging.info('Starting prob calculation process ...')
    processedVec = processVec(freqVec)
    processedMat = processMat(freqMat)
    logging.info('Writing new prob files ...')
    writeVecToFile(processedVec, config.VEC_PROB_FILE)
    writeMatToFile(processedMat, config.MAT_PROB_FILE)
    (hour, minute, second) = getTime(time.time() - tstart)
    logging.info('Successfully add new data to SLM model, time consumed: %dmin%ds' % (minute, second))

def addFreqData(fn):
    tstart = time.time()
    logging.info('Getting Hanzi from file ...')
    hanzi2Idx, idx2Hanzi = getHanziMapping('WordTable.txt')
    logging.info('Reading language material ...')
    f = open(fn, 'r')
    text = f.read().decode('utf-8')
    f.close()
    logging.info('Getting original vec freq file ...')
    freqVec = getVecFromFile(config.VEC_FREQ_FILE, type = int)
    logging.info('Getting original mat freq file ...')
    freqMat = getSparseMatFromFile(config.MAT_FREQ_FILE, type = int)
    logging.info('Append data from new material ...')
    getFreqData(text, freqVec, freqMat, hanzi2Idx, idx2Hanzi)
    logging.info('Writing new freq files ...')
    writeVecToFile(freqVec, config.VEC_FREQ_FILE)
    writeSparseMatToFile(freqMat, config.MAT_FREQ_FILE)
    (hour, minute, second) = getTime(time.time() - tstart)
    logging.info('Successfully add new freq data to SLM model, time consumed: %dmin%ds' % (minute, second))

def refresh():
    logging.info('Getting original vec freq file ...')
    freqVec = getVecFromFile(config.VEC_FREQ_FILE, type = int)
    logging.info('Getting original mat freq file ...')
    freqMat = getSparseMatFromFile(config.MAT_FREQ_FILE, type = int)
    logging.info('Starting prob calculation process ...')
    processedVec = processVec(freqVec)
    processedMat = processMat(freqMat)
    logging.info('Writing new prob files ...')
    writeVecToFile(processedVec, config.VEC_PROB_FILE)
    writeMatToFile(processedMat, config.MAT_PROB_FILE)
    logging.info('Successfully refresh SLM model.')


if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "", [])
    except getopt.GetoptError:
        print 'Command not found.'
        sys.exit()

    cmd = args[0]
    if cmd in ['build']:
        build()
        sys.exit()
    elif cmd in ['add']:
        fn = args[1]
        addData(fn)
        sys.exit()
    elif cmd in ['addf']:
        fn = args[1]
        addFreqData(fn)
        sys.exit()
    elif cmd in ['refresh']:
        refresh()
        sys.exit()
    else:
        print 'Command not found.'
        sys.exit()
