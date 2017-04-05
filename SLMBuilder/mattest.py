from slmprocessor import getVecFromFile, getMatFromFile, processMat, processVec
import config
import time
import os
import json
from slmbuilder import writeSparseMatToFile, getSparseMatFromFile, addToSparseMatFromFile, transferToSparseMatFile
def getTextSet(fn, size = float('inf')):
    f = open(fn, 'r')
    dataset = f.read().decode('utf-8').split('\n')
    f.close()
    textSet = []
    for data in dataset:
        if len(data) > 1:
            dataObj = json.loads(data)
            textSet.append(dataObj['title'].replace(' ', ''))
            textSet.append(dataObj['html'].replace(' ', ''))
    return textSet[0: min(size, len(textSet))]

trans = [[[0, 1, 1, 1], [1, 1, 0, 1]], [[1, 0, 1, 1], [1, 1, 1, 0]]]
def O0(input):
    return 0
def O1(input):
    return 1
def O2(input):
    return trans[input[0]][input[1]][0]
def O3(input):
    return trans[input[0]][input[1]][1]
def O4(input):
    return trans[input[0]][input[1]][2]
def O5(input):
    return trans[input[0]][input[1]][3]
def O6(input):
    return trans[input[2]][input[3]][0]
def O7(input):
    return trans[input[2]][input[3]][1]
def O8(input):
    return trans[input[2]][input[3]][2]
def O9(input):
    return trans[input[2]][input[3]][3]
def O10(input):
    return input[0]
def O11(input):
    return input[1]
def O12(input):
    return input[2]
def O13(input):
    return input[3]
funcs = [O0, O1, O2, O3, O4, O5, O6, O7, O8, O9, O10, O11, O12, O13]
# def dfs(chip3, n):
#     if n == 4:
#
#     else:
#         for i in range(0, 10):
#             chip3[n] = i
#             dfs(chip3, n + 1)
if __name__ == '__main__':
    # files = config.DATA_FILE_BASE
    # for file in files:
    #     textSet = getTextSet(file)
    #     f = open(file, 'w')
    #     f.write('\n'.join(textSet).encode('utf-8'))
    #     f.close()
    chip3 = []
    for i1 in range(0, 14):
        for i2 in range(0, 14):
            inputs = [[0, 0, 0, 0], [1, 0, 0, 0], [0, 1, 0, 0], [1, 1, 0, 0], [0, 0, 1, 0], [1, 0, 1, 0],
                      [0, 1, 1, 0], [1, 1, 1, 0], [0, 0, 0, 1], [1, 0, 0, 1]]
            ok = True
            outmat = []
            for (idx, input) in enumerate(inputs):
                in1 = funcs[i1](input)
                in2 = funcs[i2](input)
                o0 = trans[in1][in2][0]
                o1 = trans[in1][in2][1]
                o2 = trans[in1][in2][2]
                o3 = trans[in1][in2][3]
                output = [0, 1]
                output.append(input[0])
                output.append(input[1])
                output.append(input[2])
                output.append(input[3])
                output.append(in1)
                output.append(in2)
                output.append(O2(input))
                output.append(O3(input))
                output.append(O4(input))
                output.append(O5(input))
                output.append(O6(input))
                output.append(O7(input))
                output.append(O8(input))
                output.append(O9(input))
                output.append(o0)
                output.append(o1)
                output.append(o2)
                output.append(o3)
                outmat.append(output)
            outmatT = zip(*outmat)
            cnt = 0
            for row in outmatT:
                if list.count(list(row), 0) == 1:
                    cnt += 1
            if cnt >= 10:
                print 'i1:%d  i2:%d' % (i1, i2)

