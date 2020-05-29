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

start = timeit.default_timer()

# Function To find the keypoints using SIFT and SURF
def keypoints(image):
    img = cv2.imread(image)
    gray= cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

######################################################################################################
##    # SIFT Detector
##    detector = cv2.FeatureDetector_create("SIFT")
##    descriptor = cv2.DescriptorExtractor_create("SIFT")
##
##    kp1 = detector.detect(img)
##
##    k1, d1 = descriptor.compute(img, kp1)
##    print "Number of Keypoints for SIFT: %d" % (len(kp1))
##    print "The Descriptor for SIFT:"
##    print len(k1)
##
##    img = cv2.drawKeypoints(gray, k1,img, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
##    cv2.imwrite('siftImage.jpg', img)
######################################################################################################

    # SUFR Detector: need to configure SURF from opencv_contrib
    # surf = cv2.SURF(4000)
    # kp2, d2 = surf.detectAndCompute(gray,None,useProvidedKeypoints = False)

    # Initiate STAR detector
    orb = cv2.ORB_create()
    # find the keypoints with ORB
    kp = orb.detect(img,None)
    # compute the descriptors with ORB
    kp2, d2 = orb.compute(img, kp)
######################################################################################################
##    print "Number of Keypoints for SURF: %d" % (len(kp2))
##    print "The Descriptor for SURF:"
##    print len(d2)
######################################################################################################
    return [kp2, d2, gray]
######################################################################################################
##    img = cv2.drawKeypoints(gray, kp2,img, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
##    cv2.imwrite('surfImage.jpg', img)
######################################################################################################

def matchPair(image1, image2):
    # Get the keypoints, discriptor and the corresponding gray image
    kp1, d1, gray1 = keypoints(image1)
    kp2, d2, gray2 = keypoints(image2)

    matchObj = cv2.BFMatcher(cv2.NORM_L2, False) # default values
    matchedObj = matchObj.match(d1, d2)

##    # Thresholding 1: Sorting the distances
##    selMatchedObj = sorted(matchedObj, key = lambda x:x.distance)

    # Thresholding 2: Sum of distance by the length of distance multipled by a constant
    dist = [m.distance for m in matchedObj]
    thres_dist = (sum(dist) / len(dist)) * 0.90

    # Selcted only the points that pass the threshold
    selMatchedObj = [m for m in matchedObj if m.distance < thres_dist]

    # Return the total matches and the selected matches
    return [matchedObj, selMatchedObj]

def matching(image1, image2):
    # Get the keypoints, descriptor and the corresponding grey image for both the images
    kp1, d1, gray1 = keypoints(image1)
    kp2, d2, gray2 = keypoints(image2)

    # using the Brute Force matcher
    matchObj = cv2.BFMatcher(cv2.NORM_L2, False) # default values

    # Call Match function to match the image using descriptors
    matchedObj = matchObj.match(d1, d2)

    print("Number of Keypoints for first image is %d" % len(kp1))
    print("Number of Keypoints for second image is %d" % len(kp2))

    # Thresholding 1: Sorting the distances
    #matchedObj = sorted(matchedObj, key = lambda x:x.distance)

    # Thresholding 2: Sum of distance by the length of all multipled by a constant
    dist = [m.distance for m in matchedObj]
    thres_dist = (sum(dist) / len(dist)) * 0.90

    # Selcted only the points that pass the threshold
    matchedObj = [m for m in matchedObj if m.distance < thres_dist]

    # For plotting
    h1, w1 = gray1.shape[:2]
    h2, w2 = gray2.shape[:2]
    view = sp.zeros((max(h1, h2), w1 + w2, 3), sp.uint8)
    view[:h1, :w1, 0] = gray1
    view[:h2, w1:, 0] = gray2
    view[:, :, 1] = view[:, :, 0]
    view[:, :, 2] = view[:, :, 0]

    # Thresholding 1: take the top k values
    # for m in matchedObj[:50]:
    for m in matchedObj:
        color = tuple([sp.random.randint(0, 255) for _ in xrange(3)])
        cv2.line(view, (int(kp1[m.queryIdx].pt[0]), int(kp1[m.queryIdx].pt[1])), (int(kp2[m.trainIdx].pt[0] + w1), int(kp2[m.trainIdx].pt[1])), cv2.cv.CV_RGB(color[0],color[1],color[2]))

    cv2.imwrite('matching.jpg', view)

def allMatching(directory):
    # Get the list of files in the directory
    files = [f for f in listdir(directory) if isfile(join(directory, f))]
    # print(files)

    symDistMat = [[0 for x in range(len(files))] for y in range(len(files))]

    val = 1.0
    count = 0
    # iterate through the list, comparing every image
    # with every other image (including itself)
    for i in range(0, len(files)):
        for j in range(0, len(files)):
            if i == j:
                # store the value after scaling
                symDistMat[i][j] = 1 * 255
            else:
                # Get the selected matches and the total matches for both images (i, j): left to right match
                totalMatch1, seletedMatch1 = matchPair('images/' + files[i], 'images/' + files[j])

                # Get the selected matches and the total matches for both images (j, i): right to left match
                totalMatch2, seletedMatch2 = matchPair('images/' + files[j], 'images/' + files[i])

                finalMatch = 0
                # Select only the overlapping matches
                # this is done by checking for the keypoints in both the images
                # if you have a overlapping match, increment a counter
                for x in range(0, len(seletedMatch1)):
                    for y in range(0, len(seletedMatch2)):
                        if seletedMatch1[x].trainIdx == seletedMatch2[y].queryIdx and seletedMatch2[y].trainIdx == seletedMatch1[x].queryIdx:
                            finalMatch += 1
                val = 0

                # Taking the average of the total number of matches between two images
                # (i, j) and (j, i)
                avgTotalLength = (float(len(totalMatch1) + len(totalMatch2)) / 2)

                # Match quality is: selected matches by the toal number of matches
                val = (float(finalMatch)/avgTotalLength)

                # Store the value after scaling
                symDistMat[i][j] = val * 255

  #  cv2.normalize(np.array(symDistMat), np.array(symDistMat), 0, 255, cv2.cv.CV_MINMAX)
    cv2.imwrite('matrix.jpg', np.array(symDistMat))
    # print(np.array(symDistMat))
    return np.array(symDistMat)

# This function gives a Dendrogram with a horizontal line at the specified value (max_d)
# indicating the number of clusters
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
    cutOff = 45

    # Plot the truncated Dendrogram indicating the number of clusters formed below the specified value (max_d)
    # with x-axis having the index and y-axis having the distance
    fancy_dendrogram(Z,
    truncate_mode='lastp',  # show only the last p merged clusters
    p=45, # show only the last p merged clusters
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
    plt.savefig('scatterPlot.png')


#keypoints('ST2MainHall4050.jpg')
#matching('ST2MainHall4049.jpg', 'ST2MainHall4050.jpg')
distMatrix = allMatching('images')
hClustering(distMatrix)

stop = timeit.default_timer()
print('Time: ', stop - start)
