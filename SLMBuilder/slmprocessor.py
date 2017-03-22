# -*- coding:utf-8 -*-
import config
import math
import time

def getVecFromFile(fn, type = int, sep = ' '):
    f = open(fn, 'r')
    vec = map(type, f.read().split(sep))
    f.close()
    return vec

def getMatFromFile(fn, type = int, sepr = '\n', sepc = ' '):
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

def processVec(vec, func = math.log, precision = 4):
    tot = float(sum(vec)) + len(vec)
    newVec = [round(func((item + 1) / tot), precision) for item in vec]
    return newVec

def processMat(mat, func = math.log, precision = 4):
    size = len(mat)
    newMat = []
    for (rowIdx, row) in enumerate(mat):
        newMat.append(processVec(row))
    return newMat


if __name__ == '__main__':
    start = time.time()
    vec = getVecFromFile(config.VEC_DATA_FILE)
    mat = getMatFromFile(config.MAT_DATA_FILE)
    print processVec(vec)
    writeVecToFile(processVec(vec), config.VEC_PROB_FILE)
    writeMatToFile(processMat(mat), config.MAT_PROB_FILE)
    end = time.time()
    print 'Time: %d' % (end - start)