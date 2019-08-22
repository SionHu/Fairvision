'''
The Random number generator that helps generate image lists for phase01a and phase01b
'''

from django.conf import settings
from django.db import transaction
from django.db.models import Count
from operator import attrgetter
import random
from numpy import argmin
from ..models import Question, ImageModel, Phase

NUM_ANSWERS = 5


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
        # Create a new GET list if necesary
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

def step2_push(request):
    imgset = int(request.POST.getlist('imgnum[]')[0])
    a = Phase.objects.get(phase='2')
    a.post[imgset] += 1
    a.save()
    #Phase.rawUpdate(f'post[{imgset}]', f'post[{imgset}] + 1', "phase = '2'")

def step2_pop():
    rounds = Phase.safeget(phase='2')

    imin = -1
    getMin = 900000
    postMin = 900000
    for i, (get, post) in enumerate(zip(rounds.get, rounds.post)):
        if post < postMin:
            imin, getMin, postMin = i, get, post
        elif post == postMin and get < getMin:
            imin, getMin, postMin = i, get, post

    a = Phase.objects.get(phase='2')
    a.get[imin] += 1
    a.save()
    #Phase.rawUpdate(f'get[{imin}]', f'get[{imin}] + 1', "phase = '2'")
    return rounds.imgset[4*imin:4*imin+4], [imin], min(rounds.post) >= (Question.objects.filter(isFinal=True).count() * NUM_ANSWERS)

def getLeastAnsweredQuestions(count):
    questions = list(Question.objects.filter(isFinal=True).annotate(Count('answers')).order_by('answers__count')[:count])
    questions.reverse()
    lastIndex = -count

    for i, q in enumerate(questions):
        if q.answers.filter(step1=False).count() > NUM_ANSWERS:
            lastIndex = i
            q.isFinal = False
            q.save()
        else:
            break

    del questions[:lastIndex]
    return questions
