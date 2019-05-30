'''
The Random number generator that helps generate image lists for phase01a and phase01b
'''

from users.models import ImageModel, Rounds
from django.conf import settings
import random

KEY = settings.KEY

def pushPostList(request, phase):
    """
    Update the rounds posted for a particular phase.
    In order to do this, the list of images posted is sent
    back to the server in the 'imageIds' field of the POST
    request.
    """
    rounds = Rounds.objects.filter(phase=phase).get()
    postList = rounds.post
    postList.extend([int(i[-8:-4]) for i in request.POST.getList('imageIds')])
    rounds.post = postList
    rounds.save()

def popGetList(rounds, count=1):
    """
    Get the number of POSTed responses and the ID of the
    next image to show on the screen for a particular phase
    and return them both as a tuple. Pass in the rounds object
    if already computed by pushPostList. This assumes that count
    (usually 1 or 4) is less than the number of images.
    """
    # Get the rounds object
    getList = rounds.get

    if len(getList) < count:
        nextImage = getList
        count -= len(getList)
        # Create a new GET list if necesary
        postList = rounds.post
        print("Shuffling")
        keyPiece = KEY.rsplit('/', 1)[0]+'/'
        getList = [i.imgid for i in ImageModel.objects.filter(img__startswith=keyPiece)]
        random.shuffle(getList)
        print("Shuffled")
    else:
        nextImage = []

    # Get the next images for the round
    nextImage.extend(getList[:count])
    print("Pop "+str(count)+": "+str(nextImage))
    del getList[:count]
    print("    Now: "+str(getList))
    rounds.get = getList
    rounds.save()
    return nextImage
