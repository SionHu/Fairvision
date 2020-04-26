import numpy as np
import cv2, sys
from matplotlib import pyplot as plt

img1 = cv2.imread('images/image_0001.jpg',0)    # queryImage
img2 = cv2.imread('images/image_0002.jpg',0)    # trainImage

# Initiate SIFT detector
orb = cv2.ORB_create()

# find the keypoints and descriptors with SIFT
kp1, des1 = orb.detectAndCompute(img1,None)
kp2, des2 = orb.detectAndCompute(img2,None)

def ORBDescriptors():
    print("-- Brute-Force Matching with ORB Descriptors --")

    # create BFMatcher object
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    # Match descriptors.
    matches = bf.match(des1,des2)

    # Sort them in the order of their distance.
    matches = sorted(matches, key = lambda x:x.distance)

    # Draw first 10 matches.
    # img3 = cv2.drawMatchesKnn(img1,kp1,img2,kp2,matches,None,flags=2)
    img3 = cv2.drawMatches(img1,kp1,img2,kp2,matches[:10], None,flags=2)

    plt.imshow(img3),plt.show()

def SIFTDescriptors():
    print("-- Brute-Force Matching with SIFT Descriptors and Ratio Test --")

    # BFMatcher with default params
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1,des2, k=2)

    # Apply ratio test
    good = []
    for m,n in matches:
        if m.distance < 0.75*n.distance:
            good.append([m])

    # cv2.drawMatchesKnn expects list of lists as matches.
    img3 = cv2.drawMatchesKnn(img1,kp1,img2,kp2,good,None,flags=2)

    plt.imshow(img3),plt.show()

def FLANNMatcher():
    print("-- FLANN based Matcher --")

    # FLANN parameters
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks=50)   # or pass empty dictionary

    flann = cv2.FlannBasedMatcher(index_params,search_params)

    matches = flann.knnMatch(des1,k=2)

    # Need to draw only good matches, so create a mask
    matchesMask = [[0,0] for i in range(len(matches))]

    # ratio test as per Lowe's paper
    for i,(m,n) in enumerate(matches):
        if m.distance < 0.7*n.distance:
            matchesMask[i]=[1,0]

    draw_params = dict(matchColor = (0,255,0),
                       singlePointColor = (255,0,0),
                       matchesMask = matchesMask,
                       flags = 0)

    img3 = cv2.drawMatchesKnn(img1,kp1,img2,kp2,matches,None,**draw_params)

    plt.imshow(img3,),plt.show()

if __name__ == '__main__':
    if len(sys.argv) == 2:
        if sys.argv[1] == "1":
            ORBDescriptors()
        elif sys.argv[1] == "2":
            SIFTDescriptors()
        elif sys.argv[1] == "3":
            FLANNMatcher()
    else: print("Error: lack of command line arguments.")
