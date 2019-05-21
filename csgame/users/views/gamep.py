from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from users.models import CustomUser, ImageModel, Attribute, RoundsNum, PhaseBreak, Phase01_instruction, Phase02_instruction, Phase03_instruction

from django.contrib.auth.admin import UserAdmin

from django.http import HttpResponse

from django.shortcuts import render

import boto3
import botocore
from botocore.client import Config
import random
import json
from .roundsgenerator import rphase02

# We should set up in backend manually
KEY = settings.KEY
NUMROUNDS = settings.NUMROUNDS

@login_required
def phase01a(request):
    rounds, _ = RoundsNum.objects.get_or_create(phase='phase01a', defaults={'num': 1})
    roundsnum = rounds.num
    rounds.save()

    print("Round phase is: ", rounds.phase)

    if roundsnum > NUMROUNDS:
        # push all to waiting page
        return render(request, 'over.html', {'phase': 'PHASE 01a'})

    # Need to check 
    if request.method == 'POST':
        # Update the rounds number for phase 01a
        roundsnum = RoundsNum.objects.filter(phase='phase01a').first().num + 1
        RoundsNum.objects.filter(phase='phase01a').update(num=roundsnum)

        # Get the Q and Ans

        # Call the NLP function and get back with results, it should be something like wether it gets merged or kept 

        # If exists, update counts and put answer into the old Question 

        # If not, create a new Q&A pair and put inside


    # Single image that will be sent to front-end, will expire in 300 seconds (temporary)
    serving_img_url = default_storage.url(KEY.format(roundsnum))
    print("roundsnum is: " + roundsnum)

    # Previous question pair that will be sent to front-end 
    if roundsnum > 1 and roundsnum <= 800:
        # Get the previous question 
        previous_question = Question.objects.get(KEY.format(roundsnum-1))
        if not previous_question:
            raise Exception("The previous image does not have any question which is wired")
    return render(request, 'over.html')

# View for phase 01 b
@login_required
def phase01b(request):
    return render(request, 'over.html', {'phase': 'PHASE 01b'})

# Remove what we have for phase02
@login_required
def phase02(request):
    return render(request, 'over.html', {'phase' : 'PHASE 02'})


# View for phase3
@login_required
def phase03(request):

    
    attr = Attribute.objects.all()
    attributes = list()

    if attr.exists():
        attributes = attr
    else:
        # just send only none
        attributes = ['none']
    
    inst = Phase03_instruction.get_queryset(Phase03_instruction)
    instructions = list()
    if inst.exists():
        instructions = inst
    else: 
        instructions = ['none']
    
    # Update count
    if request.method == 'POST':
        dictionary = json.loads(request.POST['data[dict]'])
        for d in dictionary:
            # print("key: ", d, " value: ", dictionary[d])
            at = Attribute.objects.get(word=d)
            at.count += dictionary[d]
            at.save()
            
        return HttpResponse(None)
    else:
        return render(request, 'phase03.html', {'attributes': attributes, 'instructions': instructions})


