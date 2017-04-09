# 笨拼音 BenPinyin
笨拼音，基于二元字模型和三元字模型的中文拼音输入法。

## 使用方法:
进入/src文件夹下，执行python BenPinyin.py [options]命令。  
可选参数：  
* (空)    不输入额外参数，进入BenPinyin Shell，可进行交互式翻译。  
* -i <input file> -o <output file>    从输入文件中读取拼音，翻译成句子后写入出入文件。  
* -t <test file>    从测试文件中读取数据进行正确率测试。  
* --ngram=<N>    使用N元词模型，N只能为2或3，默认是2。  

## 注意事项：
1. 程序使用python2进行编写，可在windows系统和macOS系统上正常运行。
2. 由于未使用数据库，三元模型消耗的内存巨大，请保证使用 --ngram=3 参数时至少有2G空余内存。
3. 在Shell中输入exit可退出。
4. 输入文件每行一串拼音，不得有多余空行，拼音之间只能有一个空格。
5. 测试文件按照拼音一行、正确答案一行的顺序，不得有多余空行，拼音之间只能有一个空格。

## 使用实例：
* python BenPinyin.py --ngram=3    使用三元字模型，进入Shell。  
* python BenPinyin.y -i ../data/input.txt -o ../data/output.txt --ngram=3    使用三元字模型，进行文件输入输出。  
* python BenPinyin.py -t ../data/test.txt    使用二元字模型，进行正确率测试。  
/data文件夹下已经给出了可用的输入文件 input.txt 和测试文件 test.txt ，可以直接使用。  
