'''
The Random number generator that helps generate image lists for phase01a and phase01b
'''

from django.conf import settings
from django.db import transaction
import random
from users.models import ImageModel, Phase

KEY = settings.KEY


def pushPostList(request, phase):
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

    # Update the user's session variable with the old images
    old = int(request.POST['oldnum'])
    userList = request.session.get('user_imgs_phase'+phase, [])
    userList.extend(new)
    if old != -1:
        userList.append(old)
    request.session['user_imgs_phase'+phase] = userList
    print('user_imgs_phase'+phase + str(request.session['user_imgs_phase'+phase]))
    return new


@transaction.atomic
def popGetList(phase, count=1):
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
        keyPiece = KEY.rsplit('/', 1)[0]+'/'
        getList = [i for i in ImageModel.objects.filter(
            img__startswith=keyPiece).values_list('imgid', flat=True) if i not in postList]
        random.shuffle(getList)
    else:
        nextImage = []

    # Get the next images for the round
    nextImage.extend(getList[:count])
    del getList[:count]
    rounds.get = getList
    rounds.save()
    return rounds, nextImage
