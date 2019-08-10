'''
Usage: script for using the nlp server to
Data Input: list contains of Question with text + id; Corresponding Answers for each question with text + question id;
Data Output: dict that 1 answer corresponds to 1 question
'''

# impoer django settings module to make this script work separately
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "csgame.settings")
import django
django.setup()
from users.models import Question, Answer, Attribute
from django.db.models import F
from phase2_reducer import AnswerReducer
from users.views.rephrasing import rephrase

'''
script function for phase02
'''
def phase02():
    # Get all the queries for answer and question from database
    questions = Question.objects.filter(isFinal=True)
    answers = Answer.objects.all()
    # Make the list with requirements
    question_list = [[que.text, que.id] for que in questions]
    answer_list = [[ans.text, ans.question.id] for ans in answers]
    # print("answer list: ", answer_list)


    test_obj = AnswerReducer(questions=question_list, answers=answer_list)
    test_obj.grouper()
    result_dict = test_obj.reduce_within_groups()

    for q, (a, count) in result_dict.items():
        print("a is: ", a)
        Answer.objects.filter(text=a, question_id=q).update(isFinal=True, count=count)
    print("Update successfully!")

if __name__ == "__main__":
    phase02()
    # rephrase and import into attributes we have
    for answer in Answer.objects.filter(isFinal=True):
        Attribute.objects.get_or_create(word=rephrase(answer.question.text, answer.text), answer=answer)
