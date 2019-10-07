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


def pushPostList(request, phase='1'):
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
def popGetList(fullList, count=3, phase='1', recycle=False):
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
    return rounds, nextImage

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
        sets.append(imin)

    rounds.save()
    print(imgs, sets, questions)
    return imgs, sets, questions, postMin >= numQs
