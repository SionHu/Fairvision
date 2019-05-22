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
from .send_result import send_result

# We should set up in backend manually
KEY = settings.KEY
NUMROUNDS = settings.NUMROUNDS

@login_required
def phase01a(request):
    rounds, _ = RoundsNum.objects.get_or_create(phase='phase01a', defaults={'num': 1})
    roundsnum = rounds.num

    print("Round phase is: ", rounds.phase)

    if roundsnum > NUMROUNDS:
        # push all to waiting page
        return render(request, 'over.html', {'phase': 'PHASE 01a'})

    # Need to check 
    if request.method == 'POST':

        # Get the Q and Ans for the current question
        question = request.POST.get('Question')
        answer = request.POST.get('Answer')
        Ans, _ = Answer.objects.get(text=answer)
        if Ans:
            Answer.objects.filter(text=answer).update(count=Ans.count+1)
        else:
            Ans = Answer.objects.create(text=answer)
        # Call the NLP function and get back with results, it should be something like wether it gets merged or kept 
        old_Q = Question.objects.all()
        # backend call NLP and get back the results, it should be a boolean and a string telling whether the new entry will be created or not
        # exist_q should be telling which new question got merged into
        back_result, exist_q = send_result(question, old_Q)
        if back_result:
            # if the new question get merged
            newCount = Question.objects.filter(text=exist_q).first().num + 1
            Question.objects.filter(text=exist_q).update(count=newCount, isFinal=True)
            Answer.question = Question.objects.filter(text=exist_q).first()
        else:
            # If not, create a new Q&A pair in database and put inside
            new_Q = Question.objects.create(text=question) 
            new_Q.anwer_set.add(Answer.objects.get(text=answer))


        # Update the rounds number for phase 01a
        roundsnum = RoundsNum.objects.filter(phase='phase01a').first().num + 1
        RoundsNum.objects.filter(phase='phase01a').update(num=roundsnum)

    # Single image that will be sent to front-end, will expire in 300 seconds (temporary)
    serving_img_url = default_storage.url(KEY.format(roundsnum))
    print("roundsnum is: " + roundsnum)

    # Previous all question pairs that will be sent to front-end 
    if roundsnum > 1 and roundsnum <= NUMROUNDS:
        # Get the previous question 
        previous_questions = Question.objects.all()
        if not previous_questions:
            raise Exception("The previous images does not have any question which is wired")
    return render(request, 'over.html', {'url' : serving_img_url})
'''
View for phase 01 b
Output to front-end: list of all questions and 4 images without overlapping (similar to what we did before)
POST = me
'''
@login_required
def phase01b(request):

    # Only show people all the question and the answer. Keep in mind that people have the chance to click skip for different questions
    # There should be an array of question that got skipped. Each entry should the final question value
    rounds, _ = RoundsNum.objects.get_or_create(phase='phase01b', defaults={'num': 1})
    roundsnum = rounds.num
    rounds.save()

    print("Round phase is: ", rounds.phase)
    if roundsnum > RoundsNum:
        return render(request, 'over.html', {'phase' : 'PHASE 01b'})
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


