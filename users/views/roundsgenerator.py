'''
The Random number generator that helps generate image lists for phase02
def rphase02 is for phase02
'''

def rphase02(num):
    datas = list()
    for i in range(0, num):
        insertnum = 1 + 4 * i
        datas.append(insertnum)
    # print("The final datas is: ", datas)
    return datas
