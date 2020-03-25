'''
The Random number generator that helps generate image lists for phase01a and phase01b
'''

from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.db.models.expressions import Subquery
from operator import attrgetter
import random
from numpy import argmin
from ..models import Question, Answer, ImageModel, Phase


def pushPostListRandom(request, phase='A'):
    """
    Update the rounds POSTed for a particular phase.
    In order to do this, the list of images POSTed is sent
    back to the server in the 'imgnum' field of the POST
    request. Return the IDs of the images just shown to
    the user.
    """
    # Update the database with the POSTed images
    new = [int(i) for i in request.POST.getlist('imgnum[]')]
    with transaction.atomic():
        rounds = Phase.objects.select_for_update().get(phase=phase)
        postList = rounds.post
        postList.extend(new)
        rounds.post = postList
        rounds.save()

    userList = request.hit.get('user_imgs_phase'+phase, [])
    userList.extend(new)
    request.hit['user_imgs_phase'+phase] = userList
    return new


@transaction.atomic
def popGetListRandom(fullList, count=3, phase='A', recycle=False):
    """
    Get the rounds object and the ID of the next image to show
    on the screen for a particular phase and return them both
    as a tuple. This assumes that count (usually 1 or 4) is
    less than the number of images.
    """
    # Get the rounds object
    rounds = Phase.objects.select_for_update().get_or_create(phase=phase)[0]
    getList = rounds.get

    if len(getList) < count:
        nextImage = getList
        count -= len(getList)
        # Create a new GET list if necessary
        postList = rounds.post
        getList = [i for i in fullList if i not in postList and i not in nextImage]
        random.shuffle(getList)
        if recycle and len(getList) < count:
            rounds.post = []
            getList = [i for i in fullList if i not in nextImage]
            random.shuffle(getList)
    else:
        nextImage = []

    # Get the next images for the round
    nextImage.extend(getList[:count])
    del getList[:count]
    rounds.get = getList
    rounds.save()
    print(nextImage)
    return rounds, nextImage, -1, False


def pushPostListClustered(request, phase='B'):
    """
    Update the rounds POSTed for a particular phase.
    In order to do this, the list of images POSTed is sent
    back to the server in the 'imgnum' field of the POST
    request. Return the IDs of the images just shown to
    the user.
    """
    # Update the database with the POSTed images
    new = [int(i) for i in request.POST.getlist('imgnum')]
    frame = int(request.POST.get('frame'))
    with transaction.atomic():
        rounds = Phase.objects.select_for_update().get(phase=phase)
        postList = rounds.post
        postList.remove(frame)
        rounds.post = postList
        rounds.save()

    userList = request.hit.get('user_imgs_phase'+phase, [])
    userList.extend(new)
    request.hit['user_imgs_phase'+phase] = userList
    return new


def frameShuffle(clusterA, clusterB, numFrames=None):
    """
    Use the images from both clusters to create frames following
    the March 24th methodology:
    https://docs.google.com/document/d/1a-583cc3IQFbcJ8iKUN8LZlLSNQ2W45VNJo8_tyR2cU/edit
    """
    clusterA = list(clusterA)
    clusterB = list(clusterB)

    # Calculate the number of frames needed for each cluster
    # Sample calculations for list(frameShuffle(list(range(0, 84)), list(range(100, 136)))) can be found here:
    # https://docs.google.com/presentation/d/1t_VGDJjDCALTI8UkRmxegqn0ejr7iOon69J2PtKigjY/edit#slide=id.g80ff1a75ca_0_98
    if numFrames is None:
        numFrames = (len(clusterA) + len(clusterB)) // 3
    numImgAB = round(len(clusterA) * len(clusterB) / (len(clusterA) + len(clusterB)))
    numFramesA = round((numFrames * len(clusterA)) / (len(clusterA) + len(clusterB) + numImgAB))
    numFramesB = round((numFrames * len(clusterB)) / (len(clusterA) + len(clusterB) + numImgAB))
    numFramesAB = numFrames - numFramesA - numFramesB

    random.shuffle(clusterA)
    random.shuffle(clusterB)

    # generate A frames
    a = -3
    for a in range(0, 3 * numFramesA, 3):
        yield from clusterA[a:a+3]
    a += 3

    # generate B frames
    b = -3
    for b in range(0, 3 * numFramesB, 3):
        yield from clusterB[b:b+3]
    b += 3

    numImgA = round(len(clusterA) / (len(clusterA) + len(clusterB)) * (numFramesAB * 3))
    numImgB = numFramesAB * 3 - numImgA

    # generate AB frames
    numImgATaken = 0
    numImgBTaken = 0
    for i in range(3, 3 + 3 * numFramesAB, 3):
        numImgATakenNew = i * numImgA / numFramesAB / 3
        numImgBTakenNew = i * numImgB / numFramesAB / 3
        yield from clusterA[a + round(numImgATaken) : a + round(numImgATakenNew)]
        yield from clusterB[b + round(numImgBTaken) : b + round(numImgBTakenNew)]
        numImgATaken = numImgATakenNew
        numImgBTaken = numImgBTakenNew


@transaction.atomic
def popGetListClustered(clusterA, clusterB, count=3, phase='B'):
    """
    Get the rounds object and the ID of the next image to show
    on the screen for a particular phase and return them both
    as a tuple. This assumes that count (usually 1 or 4) is
    less than the number of images.
    """
    # Get the rounds object
    rounds = Phase.objects.select_for_update().get_or_create(phase=phase)[0]
    getList = rounds.get
    postList = rounds.post

    if not getList:
        getList = rounds.get = list(frameShuffle(clusterA, clusterB))
        postList = list(range((len(getList)+1) // count))
        random.shuffle(postList)
        rounds.post = postList
        rounds.save()

    if not postList:
        nextImage = []
        frame = -2
    else:
        # Take a frame from the queue and add it to the end
        frame = postList[0]
        del postList[0]
        postList.append(frame)
        rounds.post = postList
        rounds.save()

        # Get the next images for the round
        nextImage = getList[frame*count:frame*count+count]

    #print(getList)
    #print(rounds)
    #print(nextImage)
    #print(frame)
    return rounds, nextImage, frame, False

@transaction.atomic
def pushPostList(request, phase='1'):
    isRandom = int(request.POST.get('frame')) == -1

    rounds = Phase.objects.select_for_update().get_or_create(phase=phase)[0]
    getList = rounds.get
    postList = rounds.post

    getList.reverse()
    try:
        getList.remove(isRandom)
    except ValueError:
        pass
    getList.reverse()

    rounds.get = getList
    rounds.save()

    if isRandom:
        print("Random recieved")
        return pushPostListRandom(request, phase='A')
    else:
        print("Cluster recieved")
        return pushPostListClustered(request, phase='B')

@transaction.atomic
def popGetList(count=3, phase='1'):
    A = Phase.objects.select_for_update().get_or_create(phase='A')[0]
    B = Phase.objects.select_for_update().get_or_create(phase='B')[0]
    BnotAllowed = len(B.get) < 3 and len(B.post) != 0
    AnotAllowed = len(A.post) == 0
    print(AnotAllowed , BnotAllowed)
    if AnotAllowed and not BnotAllowed:
        isRandom = True
    elif not AnotAllowed and BnotAllowed:
        isRandom = False
    elif AnotAllowed and BnotAllowed:
        return None, [], -1, True
    else:
        # select one
        rounds = Phase.objects.select_for_update().get_or_create(phase=phase)[0]
        getList = rounds.get
        postList = rounds.post

        if not getList:
            numFrames = (ImageModel.objects.count()+count-1) // count
            getList = [1, 0] * numFrames
            random.shuffle(getList)
            rounds.get = getList

        isRandom = getList[0]
        del getList[0]
        getList.append(isRandom)
        rounds.get = getList
        rounds.save()

    if isRandom:
        fullList = ImageModel.objects.filter(img__startswith=settings.KEYRING).values_list('id', flat=True)
        print("Random chosen")
        return popGetListRandom(fullList, count=3, phase='A', recycle=False)
    else:
        clusterA = ImageModel.objects.filter(img__startswith=settings.KEYRING, cluster="A").values_list('id', flat=True)
        clusterB = ImageModel.objects.filter(img__startswith=settings.KEYRING, cluster="B").values_list('id', flat=True)
        print("Cluster chosen")
        return popGetListClustered(clusterA, clusterB, count=3, phase='B')

@transaction.atomic
def step2_push(request):
    imgsets = [int(i) for i in request.POST.getlist('imgnum[]')]
    a = Phase.objects.select_for_update().get(phase='2')
    for imgset in imgsets:
        a.post[imgset] += 1
    a.save()
    #Phase.rawUpdate(f'post[{imgset}]', f'post[{imgset}] + 1', "phase = '2'")
    return imgsets

@transaction.atomic
def step2_pop(count=1):
    # Create phase object if necessary
    rounds, isNew = Phase.objects.select_for_update().get_or_create(phase='2')
    if isNew:
        imgsets = list(ImageModel.objects.filter(img__startswith=settings.KEYRING).values_list('id', flat=True))
        postLen, trunLen = divmod(len(imgsets), 6)

        # Truncate shuffled list to a multiple of 4 length
        random.shuffle(imgsets)
        if trunLen:
            del imgsets[-trunLen:]
        rounds.imgset = imgsets

        # Create empty list to store image set gets
        rounds.get = [0] * postLen

        # Create empty list to store image set posts
        rounds.post = [0] * postLen
        rounds.save()
    imgs = []
    sets = []
    questions = []
    numQs = Question.objects.filter(isFinal=True).count()

    # Find the least answered image sets
    for i in range(count // 2):
        # Find minimum answered image set
        imin = -1
        getMin = 900000
        postMin = 900000
        for i, (get, post) in enumerate(zip(rounds.get, rounds.post)):
            if (post < postMin) or post == postMin and get < getMin:
                imin, getMin, postMin = i, get, post

        # If every image was answered the correct number of times, stop
        if postMin >= numQs:
            break

        # Find the first available question for the imageset
        qset = Question.objects.filter(Q(isFinal=True) & ~Q(id__in=Subquery(
            Answer.objects.filter(imgset=imin).values_list('question_id', flat=True)
        ))).order_by('?')
        questions.extend(qset[:2])

        rounds.get[imin] += 1
        imgs.append(rounds.imgset[6*imin:6*imin+6])
        sets.append(imin)
        if len(qset) > 1:
            sets.append(imin)

    rounds.save()
    print(imgs, sets, questions)
    return imgs, sets, questions, postMin >= numQs
