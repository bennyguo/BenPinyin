import config
import time
from slmbuilder import getHanziMapping, getTime
import getopt
import sys

def build():
    tstart = time.time()
    hanzi2Idx, idx2Hanzi = getHanziMapping(config.HANZI_LIST_FILE)
    gramCount = -1
    idx2Gram = []
    gram2Idx = {}
    gramFreq = []
    triGram = {}
    for file in config.DATA_FILE_BASE:
        f = open(file, 'r')
        text = f.read().decode('utf-8')
        f.close()
        textLength = len(text)
        print 'Text %s, length: %d' % (file, textLength)
        for i in range(2, textLength):
            if not (hanzi2Idx.has_key(text[i]) and hanzi2Idx.has_key(text[i - 1]) and hanzi2Idx.has_key(text[i - 2])):
                continue
            gram = text[i - 2] + text[i - 1]
            if gram2Idx.has_key(gram):
                gramFreq[gram2Idx[gram]] += 1
                if triGram[gram].has_key(text[i]):
                    triGram[gram][text[i]] += 1
                else:
                    triGram[gram][text[i]] = 1
            else:
                gramCount += 1
                idx2Gram.append(gram)
                gram2Idx[gram] = gramCount
                gramFreq.append(1)
                triGram[gram] = {text[i]: 1}
            if i % 1000000 is 0:
                print 'Progress: %f' % (float(i) / textLength)
    print 'Writing gram list file ...'
    f = open(config.GRAM_LIST_FILE_3, 'w')
    f.write(' '.join(idx2Gram).encode('utf-8'))
    f.close()
    print 'writing gram freq file ...'
    f = open(config.VEC_FREQ_FILE_3, 'w')
    f.write(' '.join(map(str, gramFreq)))
    f.close()
    print 'writing gram-hanzi mat file ...'
    f = open(config.MAT_PROB_FILE_3, 'w')
    triGramStrArr = []
    for gram in triGram:
        gramIdx = gram2Idx[gram]
        for hanzi in triGram[gram]:
            triGramStrArr.append('%d %d %d' % (gramIdx, hanzi2Idx[hanzi], triGram[gram][hanzi]))
    f.write('\n'.join(triGramStrArr))
    f.close()
    hour, minute, second = getTime(time.time() - tstart)
    print 'Finished. Time consumed: %dh%dm%ds' % (hour, minute, second)

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
    else:
        print 'Command not found.'
        sys.exit()

