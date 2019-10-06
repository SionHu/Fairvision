import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import csv

EXP_NUM = 1

# read the csv file
file  = open('./exp0{}.csv'.format(str(EXP_NUM)), "rt", encoding="utf-8")
data = csv.reader(file, delimiter=",")
matrix = [row for row in data] # read the data from the files
# cut til only precision and recall score of each row
matrix = np.delete(matrix, (0), axis=0)
matrix = np.delete(matrix, np.s_[0:3], axis=1)

file.close()

def cal_pr():
    relevent_all = matrix[len(matrix)-1][1]
    precision, recall = [], []
    retrived = 0
    count = 0
    for row in matrix:
        pre_score, rec_score = 1, 0
        if row[0] == "T": retrived += 1
        if count != 0: pre_score = retrived / (count+1)
        precision.append(pre_score)
        recall.append(int(row[1])/int(relevent_all))
        count += 1

    # for the interpolation plot
    precision_int = np.maximum.accumulate(precision[::-1])[::-1] # interplot points
    pre_int, rec_int = [], []
    for i in range(30):
        pre_int.append(precision_int[closest(recall, i/30)])
        rec_int.append(i/30)

    output_fig(pre_int, rec_int, precision, recall)

def output_fig(pre_int, rec_int, precision, recall):

    fig, ax = plt.subplots(1, 1)

    precision_int = np.maximum.accumulate(precision[::-1])[::-1] # interplot points
    # ax.plot(recall, precision, '--y') # this is the original curve
    # ax.step(recall, precision_int, '--r') # this is the interpolation curve
    ax.plot(rec_int, pre_int, "-b", label="Experimnet {} outputs".format(EXP_NUM)) # final curve

    ax.axis('equal')
    # add legends
    ax.legend(frameon=False, loc='best');
    # Set axis titles
    ax.set_xlabel("recall")
    ax.set_ylabel("precision")
    # output the figure
    plt.savefig('./pr_exp0{}'.format(str(EXP_NUM)))

def closest(lst, K):
     lst = np.asarray(lst)
     idx = (np.abs(lst - K)).argmin()
     # print(lst[idx])
     return idx

if __name__ == '__main__':
    cal_pr()
