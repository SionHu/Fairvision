'''
The Random number generator that helps generate image lists for phase01a and phase01b
'''

from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.db.models.expressions import Subquery
from operator import attrgetter
import random
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
def popGetList(fullList, count=3, phase='1', shuffle=False, recycle=False):
    """
    Get the rounds object and the ID of the next image to show
    on the screen for a particular phase and return them both
    as a tuple. This assumes that count (usually 1 or 4) is
    less than the number of images.
    """
    # Get the rounds object
    fullList = [4379, 3308, 5219, 5423, 3476, 5362, 4371, 3483, 4258, 5327, 5113, 5349, 4827, 4166, 5471, 4826, 3988, 3715, 3676, 4228, 5508, 4201, 5504, 3821, 4691, 4763, 4856, 4847, 4814, 3926, 5434, 4418, 4119, 4861, 4972, 3592, 3849, 4390, 5089, 4339, 4925, 5304, 3911, 3525, 4017, 5334, 4859, 4403, 4927, 4138, 3223, 3617, 4901, 3902, 3294, 3995, 5479, 4487, 3604, 4174, 5274, 4784, 5443, 5384, 3993, 3422, 4205, 4967, 4975, 5168, 3723, 3574, 5034, 4636, 4787, 4410, 4777, 4981, 5272, 4504, 4850, 4134, 3365, 5151, 5424, 4940, 4157, 3698, 3394, 3246, 3500, 5476, 5063, 4034, 3910, 3620, 5492, 4854, 4528, 3912, 4837, 4429, 3382, 3391, 5281, 4764, 4273, 3973, 4164, 3756, 3363, 4397, 3957, 4491, 4832, 5199, 5284, 4013, 4498, 3915, 4194, 5011, 4441, 3386, 3918, 4997, 4078, 3486, 5310, 4912, 4988, 5280, 3724, 4525, 4836, 3675, 3437, 5268, 4596, 4570, 4879, 4427, 5390, 4308, 4848, 5523, 3790, 3454, 3900, 3648, 3576, 4216, 3384, 4145, 5099, 5470, 5346, 4051, 4424, 3599, 3789, 3930, 3304, 5415, 3870, 4626, 3403, 3905, 3944, 4277, 5032, 5117, 4382, 3392, 3825, 3532, 3377, 4251, 5125, 4613, 4111, 4469, 5426, 3670, 4303, 3558, 3867, 5148, 5466, 4641, 4391, 4312, 3607, 3940, 4758, 5056, 3632, 4511, 4408, 3616, 4731, 5347, 3487, 5458, 4084, 4163, 4330, 3356, 5406, 3477, 3336, 3785, 4476, 3901, 4419, 4178, 4647, 4790, 3762, 5224, 3624, 4470, 5425, 4202, 3705, 3936, 3836, 3204, 3846, 3866, 3968, 3634, 3932, 4473, 4939, 4869, 4806, 3234, 3501, 4675, 5373, 3654, 4210, 4108, 3376, -1, 3933, 4899, -1]
    rounds = Phase.objects.select_for_update().get_or_create(phase=phase)[0]
    getList = rounds.get

    if len(getList) < count:
        nextImage = getList
        count -= len(getList)
        # Create a new GET list if necessary
        postList = rounds.post
        getList = [i for i in fullList if i not in postList and i not in nextImage]
        if shuffle:
            random.shuffle(getList)
        if recycle and len(getList) < count:
            rounds.post = []
            getList = [i for i in fullList if i not in nextImage]
            if shuffle:
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
        if len(qset) > 1:
            sets.append(imin)

    rounds.save()
    print(imgs, sets, questions)
    return imgs, sets, questions, postMin >= numQs
