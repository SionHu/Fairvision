import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import csv, random
from sklearn import metrics
from sklearn.metrics import roc_auc_score

EXP_NUM = 1
VERSION = 1

# read the csv file
file  = open('./exp0{}_data.csv'.format(str(EXP_NUM)), "rt", encoding="utf-8")
data = csv.reader(file, delimiter=",")
matrix = [row for row in data] # read the data from the files
# cut til only precision and recall score of each row
matrix = np.delete(matrix, (0), axis=0)
matrix = np.delete(matrix, np.s_[0:5], axis=1)
# for i in range(4):
matrix_curr = matrix[:, [0,3]]
print(matrix_curr, "\n")
# ind = np.argsort(matrix_curr, axis=0)
# print(ind)

arr = [1, 3, 5, 2, 4, 6]
print(np.argsort(arr))


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
        recall.append(int(row[VERSION])/int(relevent_all))
        count += 1

    # for the interpolation plot
    precision_int = np.maximum.accumulate(precision[::-1])[::-1] # interplot points
    pre_int, rec_int = [], []
    for i in range(31):
        pre_int.append(precision_int[closest(recall, i/30)])
        rec_int.append(i/30)

    output_fig(pre_int, rec_int, precision, recall)

def output_fig(pre_int, rec_int, precision, recall):
    fig, ax = plt.subplots(1, 1)

    # the following will be used as the temporary curve for experiment 2
    precision2 = [random.randint(0,29) for i in range(30)]
    precision2 = [precision2[i]/30 for i in precision2]
    precision2 =  sorted(precision2, key=float, reverse=True)
    # print(precision2)

    precision_int = np.maximum.accumulate(precision[::-1])[::-1] # interplot points
    # ax.plot(recall, precision, '--y') # this is the original curve
    # ax.step(recall, precision_int, '--r') # this is the interpolation curve
    ax.plot(rec_int, pre_int, "-b", label="Experimnet {} outputs".format(EXP_NUM)) # final curve
    plt.fill_between(rec_int, pre_int, alpha=0.2, color='b')
    # ax.plot(rec_int, precision2, "-r", label="Experimnet 2 outputs")

    ax.axis('equal')
    # add legends
    ax.legend(frameon=False, loc='best');
    # Set axis titles
    ax.set_xlabel("recall", fontsize=15)
    ax.set_ylabel("precision", fontsize=15)
    # output the figure
    plt.savefig('./pr_exp0{}_v{}'.format(str(EXP_NUM), VERSION))

def closest(lst, K):
     lst = np.asarray(lst)
     idx = (np.abs(lst - K)).argmin()
     # print(lst[idx])
     return idx

if __name__ == '__main__':
    cal_pr()
