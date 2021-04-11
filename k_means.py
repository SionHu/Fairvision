
# coding: utf-8

# In[1]:

# for loading/processing the images  
from tensorflow.keras.preprocessing.image import load_img 
from tensorflow.keras.preprocessing.image import img_to_array 
from tensorflow.keras.applications.vgg16 import preprocess_input 

# models 
from tensorflow.keras.applications.vgg16 import VGG16 
from tensorflow.keras.models import Model

# clustering and dimension reduction
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

# for everything else
import os
import numpy as np
import matplotlib.pyplot as plt
from random import randint
import pandas as pd
import pickle


# In[2]:

import cv2
import sys
import scipy as sp
from scipy.spatial import distance
import numpy as np
np.set_printoptions(threshold=np.inf) # To print the entire matrix
from os import listdir
from os.path import isfile, join
from matplotlib import pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.cluster.hierarchy import fcluster
import timeit


# In[5]:

path = r"/home/zhu690/Downloads/5dogs/"
# change the working directory to the path where the images are located
os.chdir(path)


# this list holds all the image filename
flowers = []

# creates a ScandirIterator aliased as files
with os.scandir(path) as files:
  # loops through each file in the directory
    for file in files:
        if file.name.endswith('.jpg'):
          # adds only the image files to the flowers list
            flowers.append(file.name)


# In[3]:

#5dogs set label encode
# print(len(flowers))
# labs={}
# for i in flowers:
#     typ=i.split('_')[0]
#     if typ=='n02115913':
#         labs[i]=0
#     if typ=='n02113978':
#         labs[i]=1
#     if typ=='n02115641':
#         labs[i]=2
#     if typ=='n02115913':
#         labs[i]=3
#     if typ=='n02113799':
#         labs[i]=4
# len(labs)


# In[4]:

# #show img
# img = load_img(flowers[0], target_size=(224,224))
# # convert from 'PIL.Image.Image' to numpy array
# img = np.array(img)
# reshaped_img = img.reshape(1,224,224,3)
# x = preprocess_input(reshaped_img)


# In[6]:

# load the model first and pass as an argument
model = VGG16()
model = Model(inputs = model.inputs, outputs = model.layers[-2].output)

def extract_features(file, model):
    # load the image as a 224x224 array
    img = load_img(file, target_size=(224,224))
    # convert from 'PIL.Image.Image' to numpy array
    img = np.array(img) 
    # reshape the data for the model reshape(num_of_samples, dim 1, dim 2, channels)
    reshaped_img = img.reshape(1,224,224,3) 
    # prepare image for model
    imgx = preprocess_input(reshaped_img)
    # get the feature vector
    features = model.predict(imgx, use_multiprocessing=True)
    return features


# In[7]:

data = {}
p = path
# lop through each image in the dataset
for flower in flowers:
    # try to extract the features and update the dictionary
    try:
        feat = extract_features(flower,model)
        data[flower] = feat
    # if something fails, save the extracted features as a pickle file (optional)
    except:
        with open(p,'wb') as file:
            pickle.dump(data,file)
          
# get a list of the filenames
filenames = np.array(list(data.keys()))

# get a list of just the features
feat = np.array(list(data.values()))
feat.shape

# reshape so that there are 210 samples of 4096 vectors
feat = feat.reshape(-1,4096)
feat.shape


# In[8]:

from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
data_rescaled = scaler.fit_transform(feat)


# In[9]:

#95% of variance
pca = PCA(n_components = 0.95)
pca.fit(data_rescaled)
reduced = pca.transform(data_rescaled)


# In[12]:

print('reduced features matrix: '+ str(reduced.shape))


# In[13]:

#hierarchical clustering 
def fancy_dendrogram(*args, **kwargs):
    max_d = kwargs.pop('max_d', None)
    if max_d and 'color_threshold' not in kwargs:
        kwargs['color_threshold'] = max_d
    annotate_above = kwargs.pop('annotate_above', 0)

    ddata = dendrogram(*args, **kwargs)

    if not kwargs.get('no_plot', False):
        plt.title('Hierarchical Clustering Dendrogram (truncated)')
        plt.xlabel('index or (cluster size)')
        plt.ylabel('distance')
        for i, d, c in zip(ddata['icoord'], ddata['dcoord'], ddata['color_list']):
            x = 0.5 * sum(i[1:3])
            y = d[1]
            if y > annotate_above:
                plt.plot(x, y, 'o', c=c)
                plt.annotate("%.3g" % y, (x, y), xytext=(0, -5),
                             textcoords='offset points',
                             va='top', ha='center')
        if max_d:
            plt.axhline(y=max_d, c='k')
    return ddata

def hClustering(dmatrix):

    # Link the clusters using
    Z = linkage(dmatrix, 'ward')

    # Plot the dendrogram with default values with x-axis having the index
    # and y-axis having the distance
    plt.figure(figsize=(25,10))
    plt.title('Hierarchical')
    plt.xlabel('index')
    plt.ylabel('distance')
    dendrogram(Z, leaf_rotation=90.,leaf_font_size=8.,)
    plt.savefig('dendrogram.png')

    # Setting the cutOff value, this is the distance value on the y-axis
    cutOff =50

    # Plot the truncated Dendrogram indicating the number of clusters formed below the specified value (max_d)
    # with x-axis having the index and y-axis having the distance
    fancy_dendrogram(Z,
    truncate_mode='lastp',  # show only the last p merged clusters
    p=100, # show only the last p merged clusters
    leaf_rotation=90.,
    leaf_font_size=12.,
    show_contracted=True,
    annotate_above=10,
    max_d=cutOff,)
    plt.savefig('dendrogram_kcluster.png')

    # Retrieving the clusters, passing the horizontal cut off value
    clusters = fcluster(Z, cutOff, criterion='distance')
    print("The Clusters are:")
    print(clusters)

    # After getting the clusters, plot them using scatter plots
    plt.figure(figsize=(10, 8))
    plt.scatter(dmatrix[:,0], dmatrix[:,1], c=clusters, cmap='prism')  # plot points with cluster dependent colors
    plt.savefig('hierarchical_scatterPlot.png')
    return clusters
hircluster=hClustering(reduced)


# In[17]:

groups = {}
for file, cluster in zip(filenames,hircluster):
    if cluster not in groups.keys():
        groups[cluster] = []
        groups[cluster].append(file)
    else:
        groups[cluster].append(file)
with open('hir_cluster_result.txt', 'w') as f:
    print(groups, file=f)


# In[23]:

def view_cluster(cluster):
    plt.figure(figsize = (45,45));
    # gets the list of filenames for a cluster
    files = groups[cluster]
    # only allow up to 30 images to be shown at a time
    if len(files) > 30:
        print(f"Clipping cluster size from {len(files)} to 30")
        files = files[:50]
    # plot each image in the cluster
    for index, file in enumerate(files):
        plt.subplot(10,10,index+1);
        img = load_img(file)
        img = np.array(img)
        plt.imshow(img)
        plt.axis('off')


# In[27]:

view_cluster(5)


# In[10]:

#manually select number of features
# pca = PCA(n_components=100, random_state=22)
# pca.fit(feat)
# x = pca.transform(feat)


# In[11]:

from scipy.spatial.distance import cdist
from sklearn.metrics import silhouette_score
distortions = []
inertias = []
mapping1 = {}
mapping2 = {}
silhouette=[]
K = range(2,10)
x=reduced
for k in K:
    # Building and fitting the model
    kmeanModel = KMeans(n_clusters=k).fit(x)
    kmeanModel.fit(x)
    sse=sum(np.min(cdist(x, kmeanModel.cluster_centers_,
                                        'euclidean'), axis=1)) / x.shape[0]
    distortions.append(sse)
    inertias.append(kmeanModel.inertia_)
 
    mapping1[k] = sum(np.min(cdist(x, kmeanModel.cluster_centers_,
                                   'euclidean'), axis=1)) / x.shape[0]
    mapping2[k] = kmeanModel.inertia_
    
    silhouette.append(silhouette_score(x, kmeanModel.labels_))


# In[12]:

sil_k=K[(silhouette.index(max(silhouette)))]


# In[15]:

from kneed import KneeLocator
kn = KneeLocator(K, distortions, curve='convex', direction='decreasing')
knee_k=(kn.knee)


# In[12]:

plt.plot(K, inertias, 'bx-')
plt.xlabel('Values of K')
plt.ylabel('Distortion')
plt.title('plane The Elbow Method using Distortion')
plt.show()


# In[48]:

kmeans = KMeans(n_clusters=5,n_jobs=-1, random_state=22)
kmeans.fit(reduced)


# In[51]:

y_kmeans = kmeans.predict(reduced)
plt.scatter(reduced[:, 0],reduced[:, 1], c=y_kmeans, s=50, cmap='viridis')

centers = kmeans.cluster_centers_
plt.title('kmeans cluster')
plt.scatter(centers[:, 0], centers[:, 1], c='black', s=200, alpha=0.5);


# In[13]:

kmeans.labels_


# In[16]:

#cluster dic key:index, val: filename
groups = {}
for file, cluster in zip(filenames,kmeans.labels_):
    if cluster not in groups.keys():
        groups[cluster] = []
        groups[cluster].append(file)
    else:
        groups[cluster].append(file)


# In[17]:

#check numbet of items in each cluster
print('number of cluster')
for i in groups:
    print(len(groups[i]))


# In[19]:

with open('kmeans_sil_cluster_result.txt', 'w') as f:
    print(groups, file=f)


# In[20]:

pwd


# In[25]:

#checking with true label
# for i in groups:
#     imgs=groups[i]
#     label_=[]
#     for im in imgs:
#         if im in labs.keys():
#             label_.append(labs[im])
#     print(label_)  


# In[16]:

def view_cluster(cluster):
    plt.figure(figsize = (45,45));
    # gets the list of filenames for a cluster
    files = groups[cluster]
    # only allow up to 30 images to be shown at a time
    if len(files) > 30:
        print(f"Clipping cluster size from {len(files)} to 30")
        files = files[:50]
    # plot each image in the cluster
    for index, file in enumerate(files):
        plt.subplot(10,10,index+1);
        img = load_img(file)
        img = np.array(img)
        plt.imshow(img)
        plt.axis('off')


# In[53]:

#stanford_cars (the variables is not saved. just for demo, so no need to run agian)
view_cluster(0)


# In[54]:

view_cluster(1)


# In[55]:

view_cluster(2)


# In[74]:

#Plane
view_cluster(0)


# In[75]:

view_cluster(1)


# In[76]:

view_cluster(2)


# In[26]:

#dogs
view_cluster(0)


# In[18]:

view_cluster(1)


# In[19]:

view_cluster(2)

