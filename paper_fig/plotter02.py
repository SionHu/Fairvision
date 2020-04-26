import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import csv, random
from sklearn import metrics
from sklearn.metrics import roc_auc_score

# read the csv file

file  = open('./ce_random.csv', "rt", encoding="utf-8")
data = csv.reader(file, delimiter=",")
matrix = [row for row in data] # read the data from the files
# cut til only precision and recall score of each row
matrix = np.delete(matrix, (0), axis=0)
matrix = np.delete(matrix, np.s_[0:5], axis=1)

matrix_ran = matrix[:, [2,3,4]]
print("Rando, results:\n", matrix_ran, "\n")

file.close()


file2  = open('./ce_cluster.csv', "rt", encoding="utf-8")
data2 = csv.reader(file2, delimiter=",")
matrix2 = [row for row in data2] # read the data from the files
# cut til only precision and recall score of each row
matrix2 = np.delete(matrix2, (0), axis=0)
matrix2 = np.delete(matrix2, np.s_[0:5], axis=1)

matrix_clu = matrix2[:, [2,3,4]]
print("Cluster results:\n", matrix_clu, "\n")

file2.close()

def cal_pr(matrix):
    # relevent_all = matrix[len(matrix)-1][1]
    relevent_all = len(matrix)
    precision, recall = [], []
    retrived = 0
    count = 1
    for row in matrix:
        pre_score, rec_score = 1, 0
        if row[0] == "TRUE": retrived += 1
        if count != 0: pre_score = retrived / (count)
        precision.append(pre_score)
        recall.append(int(row[1])/int(relevent_all))

        # print('precision:', pre_score, '\trecall:', retrived/relevent_all)
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
    # ax.plot(rec_int, pre_int, "-b", label="Experimnet {} outputs".format(EXP_NUM)) # final curve
    ax.plot(rec_int, pre_int, "-b", label=TYPE) # final curve
    plt.fill_between(rec_int, pre_int, alpha=0.2, color='r')
    # ax.plot(rec_int, precision2, "-r", label="Experimnet 2 outputs")

    ax.axis('equal')
    # add legends
    ax.legend(frameon=False, loc='best');
    # Set axis titles
    ax.set_xlabel("recall", fontsize=15)
    ax.set_ylabel("precision", fontsize=15)
    # output the figure
    # plt.savefig('./pr_exp0{}_v{}'.format(str(EXP_NUM), VERSION))
    plt.savefig('./pr_{}'.format(TYPE))

def closest(lst, K):
     lst = np.asarray(lst)
     idx = (np.abs(lst - K)).argmin()
     # print(lst[idx])
     return idx

if __name__ == '__main__':
    cal_pr(matrix_ran)
