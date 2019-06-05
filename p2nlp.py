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
from users.models import Question, Answer
from django.db.models import F

'''
script function for phase02
'''
def phase02():
    # Get all the queries for answer and question from database
    questions = Question.objects.all()
    answers = Answer.objects.all()
    # Make the list with requirements
    question_list = [(que.text, que.id) for que in questions]
    answer_list = [(ans.text, ans.question.id) for ans in answers]
    print("answer list: ", answer_list)
    # psudo-code
    result_dict = p2receive([question_list, answer_list])
    for q in result_dict:
        Answer.object.filter(text=result_dict[q], question=Question.objects.get(text=q)).update(isFinal=True, count=F('count') + 1)
    print("Update successfully!")

if __name__ == "__main__":
    phase02()
