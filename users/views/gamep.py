from csgame.views import over

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.db import transaction
from django.db.models.expressions import Case, F, Value, When
from users.models import CustomUser, ImageModel, Attribute, PhaseBreak, Phase01_instruction, Phase02_instruction, Phase03_instruction, TextInstruction, Question, Answer

from django.contrib.auth.admin import UserAdmin

from django.http import HttpResponse

from django.shortcuts import render

import boto3
#from operator import attrgetter, itemgetter
import csv, os
import botocore
from botocore.client import Config
import random
import requests
import json


# self-defined decorators for crowd worker and admin/staff be able to work
from ..decorators import player_required
from .roundsgenerator import pushPostList, popGetList, step2_push, step2_pop


# We should set up in backend manually
KEYRING = settings.KEYRING
OBJECT_NAME_PLURAL = settings.OBJECT_NAME_PLURAL
NUMROUNDS = settings.NUMROUNDS
PRODUCTION = settings.IS_PRODUCTION_SITE


old_csvPath = os.path.join(settings.BASE_DIR, 'Q & A - Haobo.csv')
new_csvPath = os.path.join(settings.BASE_DIR, 'test_att.csv')


from client import send__receive_data
@player_required
def phase01a(request, previewMode=False):
    # assignmentID for front-end submit javascript
    assignmentId = request.GET.get('assignmentId')
    # Need to check
    if request.method == 'POST':
        postList = pushPostList(request)

        # Get the Q and Ans for the current question, they should be at least one Q&A for all of the set
        questions = request.POST.getlist('data_q[]')
        answers = request.POST.getlist('data_a[]')

        # print("I got questions: ", questions)
        # print("I got answers: ", answers)
        # retrieve the json data for updating skip count for the previous questions
        validation_list = request.POST.getlist('data[]')

        correct_qs = []
        for q in questions:
            text=q.replace(' ', '+')
            url = f'https://api.textgears.com/check.php?text={text}&key=SFCKdx4GHmSC1j6H'
            response = requests.get(url)
            wordsC = response.json()
            # print(wordsC)
            for err in wordsC['errors']:
                bad = err['bad']
                good = err['better']
                if good:
                    q = q.replace(bad, good[0])
            correct_qs.append(q)

        # Query list for the old data in the table
        old_Qs = list(Question.objects.filter(isFinal=True).values_list('text', 'id'))
        # print("old questions", old_Qs)

        questions = Question.objects.bulk_create([Question(text=que, isFinal=False, imageID=list(ImageModel.objects.filter(id__in=postList)), hit_id=assignmentId) for que in correct_qs])
        new_Qs = [(que.text, que.id) for que in questions] #list(map(attrgetter('text', 'id'), questions)) # don't know which is better speedwise
        # print("new question", new_Qs)

        # Call the NLP function and get back with results, it should be something like wether it gets merged or kept
        # backend call NLP and get back the results, it should be a boolean and a string telling whether the new entry will be created or not
        # exist_q should be telling which new question got merged into
        acceptedList, id_merge, id_move = send__receive_data(new_Qs, old_Qs)
        id_merge = {int(k): v for k, v in id_merge.items()}
        id_move = {int(k): v for k, v in id_move.items()}
        # print("acceptedList is: ", acceptedList)
        #print("id_merge is: ", id_merge)
        # print("id_move is: ", id_move)

        Question.objects.filter(id__in=acceptedList).update(isFinal=True)
        #Question.objects.filter(id__in=[que.id for que in questions if que.id not in id_merge]).update(isFinal=True)

        # Store id_merge under mergeParent in the database
        id_merge_sql = Case(*[When(id=new, then=Value(old)) for new, old in id_merge.items()])
        Question.objects.filter(id__in=id_merge).update(mergeParent=id_merge_sql)

        answers = Answer.objects.bulk_create([Answer(question_id=id_merge.get(que.id, que.id), text=ans, hit_id=assignmentId, imgset=-1) for que, ans in zip(questions, answers)])

        with transaction.atomic():
            id_move_sql = Case(*[When(question_id=bad, then=Value(good)) for bad, good in id_move.items()])
            Answer.objects.filter(question_id__in=id_move).update(question_id=id_move_sql)
            id_move_sql = Case(*[When(id=bad, then=Value(good)) for bad, good in id_move.items()])
            Question.objects.filter(id__in=id_move).update(isFinal=False, mergeParent=id_move_sql)
            Question.objects.filter(id__in=id_move.values()).update(isFinal=True)

        return HttpResponse(status=201)

    # Get rounds played in total and by the current player
    rounds, roundsnum = popGetList(ImageModel.objects.filter(img__startswith=KEYRING).values_list('id', flat=True))

    if len(rounds.post) >= ImageModel.objects.filter(img__startswith=KEYRING).count():
        # push all to waiting page
        return over(request, 'phase01a')

    # Single image that will be sent to front-end, will expire in 300 seconds (temporary)
    # sending 4 images at a time
    data = [i.img.url for i in ImageModel.objects.filter(id__in=roundsnum)]
    data.extend([None] * (3 - len(data)))
    # print("I got: ",     serving_img_url)
    # Previous all question pairs that will be sent to front-end

    # Get all the instructions
    instructions = Phase01_instruction.get_queryset(Phase01_instruction) or ['none']

    #Get text instructions
    text_inst = TextInstruction.objects.get(phase='01a')

    # Get all of the questions
    previous_questions = list(Question.objects.filter(isFinal=True).values_list('text', flat=True))

    return render(request, 'phase01a.html', {'url': data, 'imgnum': roundsnum, 'questions': previous_questions, 'assignmentId': assignmentId, 'previewMode': previewMode, 'instructions': instructions, 'text_inst':text_inst,'PRODUCTION': PRODUCTION, 'NUMROUNDS': NUMROUNDS[phase01a.__name__], 'object': OBJECT_NAME_PLURAL})

'''
View for phase 01 b
Output to front-end: list of all questions and 4 images without overlapping (similar to what we did before)
POST = method that retrieve the QA dictionary from the crowd workers
'''
@player_required
def phase01b(request, previewMode=False):
    # Only show people all the question and the answer. Keep in mind that people have the chance to click skip for different questions
    # There should be an array of question that got skipped. Each entry should the final question value
    assignmentId = request.GET.get('assignmentId')
    if request.method == 'POST':
        # Get the answer array for different
        # Update the rounds posted for phase 01b
        imgsets = step2_push(request)
        #pushPostList(request, '²')

        # get the dictionary from the front-end back
        dictionary = json.loads(request.POST.get('data[dict]'))
        print("I got the QA dict: ", dictionary)

        for imgset, (question, answer) in zip(imgsets, dictionary):
            print("Answer: ", answer)
            # if the answer is not empty, add into database
            que = Question.objects.get(text=question, isFinal=True)
            new_Ans = Answer.objects.create(text=answer, question=que, hit_id=assignmentId, imgset=imgset)
            # Check if the question has skip count reach some threshold (5 for example), isFinal=False
            QQ = Question.objects.get(text=question, isFinal=True)
            if QQ.answers.filter(text='').count() >= 5:
                QQ.isFinal = False
                QQ.save()

        return HttpResponse(status=201)

    # Get rounds played in total and by the current player
    roundsnum, imin, questions, stopGame = step2_pop(NUMROUNDS[phase01b.__name__])
    questions = [q.text for q in questions]

    if stopGame or not questions:
        return over(request, 'phase01b')

    # sending 4 images at a time
    data = [[i.img.url for i in ImageModel.objects.filter(id__in=rounds)] for rounds in roundsnum]
    data.extend([None] * (4 - len(data)))

    # Get all the insturctions sets
    instructions = Phase02_instruction.get_queryset(Phase02_instruction) or ['none']

    #Get text instructions
    text_inst = TextInstruction.objects.get(phase='01b')

    #allQuestions = dict(Question.objects.filter(id__in=[*ids for ids in questions]).values_list('id', 'text'))
    #questions = [[allQuestions[id] for id in ids] for ids in questions]

    return render(request, 'phase01b.html', {'phase': 'PHASE 01b', 'image_url' : data, 'imgnum': imin, 'question_list' : questions, 'assignmentId': assignmentId, 'previewMode': previewMode, 'instructions': instructions, 'text_inst':text_inst, 'PRODUCTION': PRODUCTION})
    # The NLP server will be updated later?

# function that should be accessible only with admin
@player_required
def phase02(request, previewMode=False):
    if request.user.is_superuser or request.user.is_staff:
        print("This is admin")
        information = "Please press the button to process the redundant answers for each questions"
    else:
        print("The user should not process the homepage")
        information= "Thank you for your support and please wait until we finish process and release the next phase"
    return render(request, 'over.html', {'info' : information})
# View for phase3
@player_required
def phase03(request, previewMode=False):
    # Update count
    if request.method == 'POST':
        words = request.POST.getlist('data[]')
        Attribute.objects.filter(word__in=words).update(count=F('count')-1)

        return HttpResponse(status=201)
    else:
        assignmentId = request.GET.get('assignmentId')
        attributes = list(Attribute.objects.values_list('word', flat=True))
        instructions = Phase03_instruction.get_queryset(Phase03_instruction) or ['none']
        return render(request, 'phase03-update.html', {'statements': attributes, 'instructions': instructions, 'assignmentId': assignmentId, 'previewMode': previewMode, 'PRODUCTION': PRODUCTION})
