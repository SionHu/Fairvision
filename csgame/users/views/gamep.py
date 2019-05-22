from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from users.models import CustomUser, ImageModel, Attribute, RoundsNum, PhaseBreak, Phase01_instruction, Phase02_instruction, Phase03_instruction, Question, Answer

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

        # Get the Q and Ans for the current question, they should be at least one Q&A for all of the set
        questions = request.POST.getlist('Questions')
        answers = request.POST.getlist('Answers')

        # retrieve the json data for updating skip count for the previous questions
        dictionary = json.loads(request.POST['data[dict]'])
        for d in dictionary:
            # print("key: ", d, " value: ", dictionary[d])
            old_Q = Question.objects.get(word=d)
            old_Q.skipCount += dictionary[d]
            old_Q.save()

        # Query list for the old data in the table
        old_Q_list = Question.objects.values_list('text', 'id')
        print("I got old_Q_list: ")
        print(old_Q_list)

        answers = Answer.objects.bulk_create([Answer(text=ans) for ans in new_answers])
        print("Well bulk answer objects", answers)

        new_Qs = []
        for que in new_questions:
            new_Q = Question.objects.create(text=que, isFinal=False)
            new_Qs.append([new_Q.text, new_Q.id])
        print("I got all the new_Q list: ", new_Qs)


        # Call the NLP function and get back with results, it should be something like wether it gets merged or kept 
        # backend call NLP and get back the results, it should be a boolean and a string telling whether the new entry will be created or not
        # exist_q should be telling which new question got merged into
        back_result_query = send_result([new_Qs, old_Q_list])
        if back_result_query is not none:
            for entry in back_result_query:
                Question.objects.filter(id=entry[0]).update(isFinal=False)
                Question.objects.filter(id=entry[1]).update(isFinal=True)
                Question.answer_set.add(answers)


        # Update the rounds number for phase 01a
        roundsnum = RoundsNum.objects.filter(phase='phase01a').first().num + 1
        RoundsNum.objects.filter(phase='phase01a').update(num=roundsnum)

    # Single image that will be sent to front-end, will expire in 300 seconds (temporary)
    serving_img_url = default_storage.url(KEY.format(roundsnum))
    print(serving_img_url)
    # Previous all question pairs that will be sent to front-end 
    if roundsnum >= 1 and roundsnum <= NUMROUNDS:
        # Get the previous question 
        previous_questions = Question.objects.all() or ["oh yeah!"]
        print("previous_questions is: ", previous_questions)
        if not previous_questions:
            raise Exception("The previous images does not have any question which is wired")
    return render(request, 'over.html', {'url' : serving_img_url, 'questions': previous_questions })
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

    data = []
    for i in range(0, 4):
        data.append(default_storage.url(KEY.format(4 * (roundsnum - 1) + i)))

    if roundsnum > NUMROUNDS:
        return render(request, 'over.html', {'phase' : 'PHASE 01b'})

    if request.method == 'POST':
        # Get the answer array for different 
        # Update the rounds number for phase 01b
        roundsnum = RoundsNum.objects.filter(phase='phase01b').first().num + 1
        RoundsNum.objects.filter(phase='phase01b ').update(num=roundsnum)
        # get the dictionary from the front-end back
        dictionary = json.loads(request.POST['data[dict'])
        for d in dictionary:
            if not dictionary[a]:
                skipc = Question.objects.get(text=d).skipCount
                Question.objects.filter(text=d).update(skipCount=skipc)
            else:
                new_Ans = Answer.objects.create(text=dictionary[d])
                new_Ans.question = Question.objects.get(text=d)

    questions = Question.objects.all()
    return render(request, 'over.html', {'phase': 'PHASE 01b', 'image_url' : data, 'quetion_list' : questions})
    # The NLP server will be updated later?

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


