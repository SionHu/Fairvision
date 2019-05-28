from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.db.models import F
from users.models import CustomUser, ImageModel, Attribute, RoundsNum, PhaseBreak, Phase01_instruction, Phase02_instruction, Phase03_instruction, Question, Answer

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
from .roundsgenerator import rphase02


# We should set up in backend manually
KEY = settings.KEY
NUMROUNDS = settings.NUMROUNDS


old_csvPath = os.path.join(settings.BASE_DIR, 'Q & A - Haobo.csv')
new_csvPath = os.path.join(settings.BASE_DIR, 'test_att.csv')


from client import send__receive_data
#@login_required
def phase01a(request):

    ''' Test case 
    old_Q = list(Question.objects.filter(isFinal=True).values_list('text', 'id'))
    new_Q = list(Question.objects.filter(isFinal=False).values_list('text', 'id'))
    result_array, id_merge = send__receive_data([new_Q, old_Q])
    # print("I got result array: ", result_array)
    print("I got the merge id: ", id_merge)
    if id_merge:
            for entry in id_merge:
                Question.objects.filter(id=id_merge[entry]).update(isFinal=False)
                Question.objects.filter(id=entry).update(isFinal=True)
    '''

    # Need to check 
    if request.method == 'POST':
        # Update the rounds number for phase 01a
        roundsnum = RoundsNum.objects.filter(phase='phase01a').first().num + 1
        RoundsNum.objects.filter(phase='phase01a').update(num=roundsnum)

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
        print(old_Qs)

        questions = Question.objects.bulk_create([Question(text=que, isFinal=False, imageID=KEY.format(roundsnum - 1)) for que in questions])
        new_Qs = [(que.text, que.id) for que in questions] #list(map(attrgetter('text', 'id'), questions)) # don't know which is better speedwise
        answers = Answer.objects.bulk_create([Answer(question=que, text=ans) for que, ans in zip(questions, answers)])        
        print(new_Qs)
        # Call the NLP function and get back with results, it should be something like wether it gets merged or kept 
        # backend call NLP and get back the results, it should be a boolean and a string telling whether the new entry will be created or not
        # exist_q should be telling which new question got merged into
        result_array, id_merge = send__receive_data([new_Qs, old_Qs])
        print("I got result array: ", result_array)
        print("I got the merge id: ", id_merge)

        if id_merge is not None:
            Question.objects.filter(id__in=[id for _, id in id_merge]).update(isFinal=True)
            ques_merge = {que.id:que for que in Question.objects.filter(id__in=id_merge.values())}
        # Don't think this is necessary. Need to test though
        #for old, new in id_merge.items():
        #    Question.objects.filter(id=old).update(isFinal=False)
        #    Question.objects.filter(id=new).update(isFinal=True)
            answers = Answer.objects.bulk_create([Answer(question=(ques_merge[id_merge[que.id]] if que.id in id_merge else que), text=ans) for que, ans in zip(questions, answers)])
        # print("Well bulk answer objects", answers)
    else:
        rounds, _ = RoundsNum.objects.get_or_create(phase='phase01a', defaults={'num': 1})
        roundsnum = rounds.num

    if roundsnum > NUMROUNDS:
        # push all to waiting page
        return render(request, 'over.html', {'phase': 'PHASE 01a'})
    
    # Single image that will be sent to front-end, will expire in 300 seconds (temporary)
    serving_img_url = default_storage.url(KEY.format(roundsnum)) or "https://media.giphy.com/media/noPodzKTnZvfW/giphy.gif"
    print("I got: ", serving_img_url)
    # Previous all question pairs that will be sent to front-end 
    if roundsnum > 1 and roundsnum <= NUMROUNDS:
        # Get the previous question of the image with roundID
        print("roundNum: ", roundsnum)
        print("key format: ", KEY.format(roundsnum-1))
        previous_questions = Question.objects.filter(imageID=KEY.format(roundsnum-1))
        if not previous_questions:
            raise Exception("The previous images does not have any question which is wired")
        return render(request, 'phase01a.html', {'url' : serving_img_url, 'questions': previous_questions })
    else:  
        return render(request, 'phase01a.html', {'url' : serving_img_url, })
'''
View for phase 01 b
Output to front-end: list of all questions and 4 images without overlapping (similar to what we did before)
POST = me
'''
#@login_required
def phase01b(request):

    # Only show people all the question and the answer. Keep in mind that people have the chance to click skip for different questions
    # There should be an array of question that got skipped. Each entry should the final question value

    if request.method == 'POST':
        # Get the answer array for different 
        # Update the rounds number for phase 01b
        roundsnum = RoundsNum.objects.filter(phase='phase01b').first().num + 1
        RoundsNum.objects.filter(phase='phase01b ').update(num=roundsnum)
        # get the dictionary from the front-end back
        dictionary = json.loads(request.POST['data[dict'])
        for question, answer in dictionary.items():
            if answer:
                new_Ans = Answer.objects.create(text=answer)
                new_Ans.question = Question.objects.get(text=question)
            else:
                Question.objects.filter(text=question).update(skipCount=F('skipCount'))
    else:
        rounds, _ = RoundsNum.objects.get_or_create(phase='phase01b', defaults={'num': 1})
        roundsnum = rounds.num

    if roundsnum > NUMROUNDS:
        return render(request, 'over.html', {'phase' : 'PHASE 01b'})

    data = [default_storage.url(KEY.format(4 * (roundsnum - 1) + i)) for i in range(0, 4)]

    questions = Question.objects.all()
    return render(request, 'over.html', {'phase': 'PHASE 01b', 'image_url' : data, 'quetion_list' : questions})
    # The NLP server will be updated later?

# Remove what we have for phase02
#@login_required
def phase02(request):

    return render(request, 'over.html', {'phase' : 'PHASE 02'})


# View for phase3
#@login_required
def phase03(request):
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
        return render(request, 'phase03.html', {'attributes': attributes, 'instructions': instructions})
