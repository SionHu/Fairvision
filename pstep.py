'''
Usage: script for using the nlp server to
Data Input: list contains of Question with text + id; Corresponding Answers for each question with text + question id;
Data Output: dict that 1 answer corresponds to 1 question
'''

# impoer django settings module to make this script work separately
import os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "csgame.settings")
os.environ.setdefault("SPACY_WARNING_IGNORE", "W008")
import django
django.setup()
from users.models import Question, Answer, Attribute
from distutils.util import strtobool
import warnings

def prestep2():
    '''
    This command calls the NLP server and reroutes new questions to the old questions in the
    database. In the current version, this happens automatically during Step 1. This piece
    of code resets the 
    '''
    from django.db import transaction
    from django.db.models.expressions import Case, F, Value, When
    from app import _reduce
    #Answer.objects.update(question_id=F('id')-1192+157)
    #Question.objects.update(mergeParent=0, isFinal=False)

    for newQ in Question.objects.filter(isFinal=False):
        old_Qs = list(Question.objects.filter(isFinal=True).values_list('text', 'id'))
        f = _reduce(new_ques=[[newQ.text, newQ.id]], old_ques=old_Qs)
        acceptedList, id_merge, id_move = f
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

        answers = [newQ.answers.first()]

        with transaction.atomic():
            id_move_sql = Case(*[When(question_id=bad, then=Value(good)) for bad, good in id_move.items()])
            Answer.objects.filter(question_id__in=id_move).update(question_id=id_move_sql)
            id_move_sql = Case(*[When(id=bad, then=Value(good)) for bad, good in id_move.items()])
            Question.objects.filter(id__in=id_move).update(isFinal=False, mergeParent=id_move_sql)
            Question.objects.filter(id__in=id_move.values()).update(isFinal=True)


def prestep3():
    '''
    This command runs the answer reduction NLP algorithm and then rephrases the QA pairs into
    statements. These statements are then shown to the user on step 3.
    '''
    from users.reducer.answers import dry_run
    from users.reducer.rephrasing import rephrase_old as rephrase

    for q, (a, count) in dry_run().items():
        print("a is: ", a)
        Answer.objects.filter(text=a, question_id=q)[:1].update(isFinal=True, count=count)

    # rephrase and import into attributes we have
    for answer in Answer.objects.filter(isFinal=True):
        try:
            Attribute.objects.get_or_create(word=rephrase(answer.question.text, answer.text), answer=answer)
        except:
            warnings.warn(f"Issue creating Attribute {answer.id}")

if __name__ == "__main__":
    def _dcap(s):
        return s[0].lower() + s[1:]

    import argparse
    parser = argparse.ArgumentParser(
        description='''This command Preprocesses a STEP of the workflow. It finalizes the contents
                       of the previous step and gets the database ready for the next step. Once this
                       command is run, there is no easy way to go back to the previous step of the
                       workflow without loosing some data.''',
        epilog=f'Preprocessing is handled differently for each step. In step 3, {_dcap(prestep3.__doc__.strip())}')

    subparsers = parser.add_subparsers(metavar='step', dest='command')

    parser.add_argument('step', type=int, default=3, choices=[3], nargs='?', help='step to preprocess (the step that you are going to start)')
    parser.add_argument('-f', '--force', type=bool, metavar='force', default=False, help='HIT id to show assignments for.')

    options = parser.parse_args()

    if options.step == 2:
        pass
    else:
        if Attribute.objects.exists():
            force = False
            if not force and sys.stdin.isatty():
                print('This script will delete all existing attributes currently on Step 3.')
                force = strtobool(input("Are you REALLY sure you want to delete the data? "))
            if force:
                Attribute.objects.all().delete()
                Answer.objects.update(isFinal=False, count=0)
            else:
                print('Existing attributes were found. Please backup this data and delete it.', file=sys.stderr)
                exit(1)
        prestep3()
