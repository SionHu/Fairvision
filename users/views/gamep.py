from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.db.models import F
from users.models import CustomUser, ImageModel, Attribute, PhaseBreak, Phase01_instruction, Phase02_instruction, Phase03_instruction, Question, Answer

from django.contrib.auth.admin import UserAdmin

from django.http import HttpResponse

from django.shortcuts import render

import boto3
#from operator import attrgetter, itemgetter
import csv, os
import botocore
from botocore.client import Config
import random
import json

# self-defined decorators for crowd worker and admin/staff be able to work
from ..decorators import player_required
from .roundsgenerator import popGetList, pushPostList


# We should set up in backend manually
KEY = settings.KEY
NUMROUNDS = settings.NUMROUNDS


old_csvPath = os.path.join(settings.BASE_DIR, 'Q & A - Haobo.csv')
new_csvPath = os.path.join(settings.BASE_DIR, 'test_att.csv')


from client import send__receive_data
@player_required
def phase01a(request):
    # assignmentID for front-end submit javascript
    assignmentId = request.GET.get('assignmentId')
    # Need to check
    if request.method == 'POST':
        postList = pushPostList(request, '01a')

        # Get the Q and Ans for the current question, they should be at least one Q&A for all of the set
        questions = request.POST.getlist('data_q[]')
        answers = request.POST.getlist('data_a[]')

        questions = [s[3:] for s in questions] # strip off 'Q: ' # map(itemgetter(slice(3, None)), questions)
        answers = [a[3:-1] for a in answers] # strip off 'A: ' and period # map(itemgetter(slice(3, -1)), answers)
        print("I got questions: ", questions)
        print("I got answers: ", answers)
        # retrieve the json data for updating skip count for the previous questions
        dictionary = json.loads(request.POST['validation[dict]'])
        print("the dictionary of life: ", dictionary)


        for text, count in dictionary.items():
            Question.objects.filter(text=text).update(skipCount=F('skipCount')-count)

        # Query list for the old data in the table
        old_Qs = list(Question.objects.values_list('text', 'id'))
        # print(old_Qs)

        questions = Question.objects.bulk_create([Question(text=que, isFinal=False, imageID=KEY.format(int(postList[-1]))) for que in questions])
        new_Qs = [(que.text, que.id) for que in questions] #list(map(attrgetter('text', 'id'), questions)) # don't know which is better speedwise
        answers = Answer.objects.bulk_create([Answer(question=que, text=ans) for que, ans in zip(questions, answers)])
        # print(new_Qs)

        # Call the NLP function and get back with results, it should be something like wether it gets merged or kept
        # backend call NLP and get back the results, it should be a boolean and a string telling whether the new entry will be created or not
        # exist_q should be telling which new question got merged into
        id_merge = send__receive_data(new_Qs, old_Qs)
        print("id_merge is: ", id_merge)

        if id_merge is not None:
            Question.objects.filter(id__in=id_merge).update(isFinal=True)
            ques_merge = {que.id:que for que in Question.objects.filter(id__in=id_merge.values())}
        # Don't think this is necessary. Need to test though
        #for old, new in id_merge.items():
        #    Question.objects.filter(id=old).update(isFinal=False)
        #    Question.objects.filter(id=new).update(isFinal=True)
            answers = Answer.objects.bulk_create([Answer(question=(ques_merge[id_merge[que.id]] if que.id in id_merge else que), text=ans) for que, ans in zip(questions, answers)])
        # print("Well bulk answer objects", answers)

        return HttpResponse(status=201)

    # Get rounds played in total and by the current player
    rounds, (roundsnum,) = popGetList('01a')
    players_images = request.session.get('user_imgs_phase01a', [])

    if len(rounds.post) > NUMROUNDS:
        # push all to waiting page
        return render(request, 'over.html', {'phase': 'PHASE 01a'})

    # Single image that will be sent to front-end, will expire in 300 seconds (temporary)
    serving_img_url = default_storage.url(KEY.format(roundsnum)) or "https://media.giphy.com/media/noPodzKTnZvfW/giphy.gif"
    # print("I got: ",     serving_img_url)
    # Previous all question pairs that will be sent to front-end

    # Get the last image not seen by the current player
    for new in reversed(rounds.post):
        if new not in players_images:
            break
    else: # if not broken
        return render(request, 'phase01a.html', {'url' : serving_img_url, 'imgnum': roundsnum, 'oldnum': -1, 'questions': []})

    # Get all of the questions for that image
    previous_questions = list(Question.objects.filter(imageID=KEY.format(new)).values('text',))
    assert previous_questions, "The previous image does not have any questions which is weird."
    return render(request, 'phase01a.html', {'url': serving_img_url, 'imgnum': roundsnum, 'oldnum': new, 'questions': previous_questions, 'assignmentId': assignmentId })

'''
View for phase 01 b
Output to front-end: list of all questions and 4 images without overlapping (similar to what we did before)
POST = method that retrieve the QA dictionary from the crowd workers
'''
@player_required
def phase01b(request):
    # Only show people all the question and the answer. Keep in mind that people have the chance to click skip for different questions
    # There should be an array of question that got skipped. Each entry should the final question value
    assignmentId = request.GET.get('assignmentId')
    if request.method == 'POST':
        # Get the answer array for different
        # Update the rounds posted for phase 01b
        pushPostList(request, '01b')

        # get the dictionary from the front-end back
        dictionary = json.loads(request.POST['data[dict]'])
        for question, answer in dictionary.items():
            # if the answer is not empty, add into database
            if not answer:
                que = Question.objects.get(text=question)
                new_Ans = Answer.objects.create(text=answer, question=que)
            else:
                Question.objects.filter(text=question).update(skipCount=F('skipCount')+1)

    # Get rounds played in total and by the current player
    rounds, roundsnum = popGetList('01b', 4)

    if len(rounds.post) > NUMROUNDS:
        return render(request, 'over.html', {'phase' : 'PHASE 01b'})

    # sending 4 images at a time
    data = [default_storage.url(KEY.format(i)) for i in roundsnum]
    questions = list(Question.objects.values('text',))
    return render(request, 'phase01b.html', {'phase': 'PHASE 01b', 'image_url' : data, 'imgnum': roundsnum, 'question_list' : questions, 'assignmentId': assignmentId})
    # The NLP server will be updated later?

# function that should be accessible only with admin
@player_required
def phase02(request):
    if request.user.is_superuser or request.user.is_staff:
        print("This is admin")
        information = "Please press the button to process the redundant answers for each questions"
    else:
        print("The user should not process the homepage")
        information= "Thank you for your support and please wait until we finish process and release the next phase"
    return render(request, 'over.html', {'info' : information})
# View for phase3
@player_required
def phase03(request):
    assignmentId = request.GET.get('assignmentId')
    attributes = Attribute.objects.all() or ['none']
    instructions = Phase03_instruction.get_queryset(Phase03_instruction) or ['none']

    # Update count
    if request.method == 'POST':
        dictionary = json.loads(request.POST['data[dict]'])
        for word, count in dictionary.items():
            # print("key: ", word, " value: ", count)
            Attribute.objects.filter(word=word).update(count=F('count')+count)

        return HttpResponse(None)
    else:
        return render(request, 'phase03.html', {'statements': attributes, 'instructions': instructions, 'assignmentId': assignmentId})
