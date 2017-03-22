from slmprocessor import getVecFromFile, getMatFromFile, processMat, processVec
import config
import time
from slmbuilder import getTextSet
if __name__ == '__main__':
    textSet = getTextSet('2016-06.txt')
    print textSet[0]
    # textSet = getTextSet('2016-01.txt')
    # print textSet[0][0]
    # mat = getMatFromFile(config.MAT_DATA_FILE, type=str)
    # newMat = []
    # cnt = 0
    # for (rowIdx, row) in enumerate(mat):
    #     for (colIdx, item) in enumerate(row):
    #         if item is not '0':
    #             cnt += 1
    #             newMat.append('%d %d %s' % (rowIdx, colIdx, item))
    # f = open('newMatFile', 'w')
    # f.write('\n'.join(newMat))
    # f.close()
    # print 'Tot: %d' % (cnt)
    # t1 = time.time()
    # mat1 = getMatFromFile(config.MAT_PROB_FILE, type=float)
    # print 'Get prob data, time: %d' % (time.time() - t1)
    #
    # t1 = time.time()
    # f = open('newMatFile', 'r')
    # mat2 = [[0 for i in range(7000)] for i in range(7000)]
    # items = f.read().split('\n')
    # print 'Load original and ini mat, time: %d' % (time.time() - t1)
    # t1 = time.time()
    # for item in items:
    #     data = map(int, item.split(' '))
    #     mat2[data[0]][data[1]] = data[2]
    # print 'Load data, time: %d' % (time.time() - t1)
    # t1 = time.time()
    # processMat(mat2)
    # f.close()
    # print 'Calc and smooth, time: %d' % (time.time() - t1)
