#!/usr/bin/env python

# impoer django settings module to make this script work separately
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "csgame.settings")
from pprint import pprint

from django.conf import settings
from csgame.storage_backends import mturk
#number of rounds that will be hard coded for other test
roundsnum = settings.NUMROUNDS

# getting arguments and steps
import sys
import argparse

from datetime import datetime

hitDescriptions = {
    'step01': "Generating questions and answers and verifying question given a shown image",
    'step02': "Given 4 images of same single object and list of questions, answer all the questions that you think are meaningful",
    'step03': "Vote YES or NO for question provided based on common sense",
}

qualificationTypes = {
    'step01': '35TOCVOB5FZ8HBFUODU53NUZ7JM230',
    'step02': '35TOCVOB5FZ8HBFUODU53NUZ7JM230',
    'step03': '35TOCVOB5FZ8HBFUODU53NUZ7JM230',
}

'''
create hits assignments with step01, step02 and available rounds number
create hits assigmments with step03 only with MaxAssignments defined by us.(Like 60?)
input: step round number
output: HITID and HIITGroupID for preview link
'''
def create_hit(step, number):
    # step 1
    for i in range(number):
        if(step == 'step01'):
            try:
                question = open(file='csgame/hitData/hitp1.xml', mode='r').read()
            except:
                print()
                print("----------------------")
                print('Error: no file found!')
                exit(1)
            # create new hit
            new_hit = mturk.create_hit(
                Title="Image Labeling With Text",
                Description=hitDescriptions['step01'],
                Keywords='image, tagging, machine learning, text generation',
                Reward = '0.50',
                MaxAssignments=1,
                LifetimeInSeconds=60*60*24*10,
                AssignmentDurationInSeconds=35*60,
                AutoApprovalDelayInSeconds=60*60*24*3,
                Question=question,
                QualificationRequirements=[
                    {
                        # this id is used on sandbox only
                        'QualificationTypeId': qualificationTypes['step01'],
                        'Comparator': 'GreaterThanOrEqualTo',
                        'IntegerValues':[60],
                        'ActionsGuarded': 'Accept',
                    }
                ]
            )
        # step 02
        elif(step == 'step02'):
            try:
                question = open(file='csgame/hitData/hitp2.xml', mode='r').read()
            except:
                print()
                print("----------------------")
                print('Error: no file found!')
                exit(1)
            # create new hit
            new_hit = mturk.create_hit(
                Title="Knowledge Answer With Image",
                Description=hitDescriptions['step02'],
                Keywords='image, tagging',
                Reward = '0.50',
                MaxAssignments=1,
                LifetimeInSeconds=60*60*24*10,
                AssignmentDurationInSeconds=35*60,
                AutoApprovalDelayInSeconds=60*60*24*3,
                Question=question,
                QualificationRequirements=[
                    {
                        'QualificationTypeId': qualificationTypes['step02'],
                        'Comparator': 'GreaterThanOrEqualTo',
                        'IntegerValues':[60],
                        'ActionsGuarded': 'Accept',
                    }
                ]
            )
        else:
            # step 03
            try:
                question = open(file='csgame/hitData/hitp3.xml', mode='r').read()
            except:
                print()
                print("----------------------")
                print('Error: no file found!')
                exit(1)
            # create new hit
            new_hit = mturk.create_hit(
                Title="Binary Selection Question",
                Description=hitDescriptions['step03'],
                Keywords='binary tagging, text verification, computer vision, machine learning',
                Reward = '0.25',
                MaxAssignments=1,
                LifetimeInSeconds=60*60*24*10,
                AssignmentDurationInSeconds=600,
                AutoApprovalDelayInSeconds=60*60*24*3,
                Question=question,
                QualificationRequirements=[
                    {
                        'QualificationTypeId': qualificationTypes['step03'],
                        'Comparator': 'GreaterThanOrEqualTo',
                        'IntegerValues':[60],
                        'ActionsGuarded': 'Accept',
                    }
                ]
            )

        # some print function for reference
        print(f"https://worker{'sandbox' if 'sandbox' in settings.MTURK_URL else ''}.mturk.com/mturk/preview?groupId={new_hit['HIT']['HITGroupId']}")
        print(f"HITID = {new_hit['HIT']['HITId']} (Use to Get Results)")

'''
check available hit
input argument: N/A
output print: HIT and Some title
'''
def print_hit():
    pprint(mturk.list_hits()['HITs'])

'''
delete_hit for different
input argument: step number
output print: delete HIT ID, Status and delete message: success or fail
Note: This should only been done for sandbox(development) or between the step gap
'''
def delete_hit(step):
    # Delete all HITs for now
    for item in mturk.list_hits()['HITs']:
        hit_id=item['HITId']
        print('HITId:', hit_id)

        # GET the HIT status
        status = mturk.get_hit(HITId=hit_id)['HIT']['HITStatus']
        print('HITStatus: ', status)
        description = mturk.get_hit(HITId=hit_id)['HIT']['Description']

        # delete step01
        if step == 'step01' and description == hitDescriptions['step01']:
            # If HIT is active then set it to expire immediately
            if status=='Assignable':
                response = mturk.update_expiration_for_hit(
                    HITId=hit_id,
                    ExpireAt=datetime(2015, 1, 1)
                )
            if status == 'Unassignable':
                try:
                    response = mturk.update_expiration_for_hit(
                        HITId=hit_id,
                        ExpireAt = datetime(2015, 1, 1)
                    )
                except Exception as e:
                    print(e)
            # Delete the HIT
            try:
                mturk.delete_hit(HITId=hit_id)
            except Exception as e:
                # print(e)
                print('Not deleted')
            else:
                print('Deleted')
        elif step == 'step02' and description == hitDescriptions['step02']:

            # If HIT is active then set it to expire immediately
            if status=='Assignable':
                response = mturk.update_expiration_for_hit(
                    HITId=hit_id,
                    ExpireAt=datetime(2015, 1, 1)
                )

            print("I found for step2")
            # Delete the HIT
            try:
                mturk.delete_hit(HITId=hit_id)
            except:
                print('Not deleted')
            else:
                print('Deleted')
        elif step == 'step03' and description == hitDescriptions['step03']:
            # If HIT is active then set it to expire immediately
            if status=='Assignable':
                response = mturk.update_expiration_for_hit(
                    HITId=hit_id,
                    ExpireAt=datetime(2015, 1, 1)
                )

            print("I found for step3")
            # Delete the HIT
            try:
                mturk.delete_hit(HITId=hit_id)
            except:
                print('Not deleted')
            else:
                print('Deleted')

'''
check completed assigmments
input argument: hit
output print: HIT and Some title
'''
def print_assignment(hit_id):
    if hit_id == 'all':
        a = []
        for hit in mturk.list_hits()['HITs']:
            try:
                a.extend(mturk.list_assignments_for_hit(
                    HITId=hit['HITId']
                ).get('Assignments', []))
            except Exception as e:
                print(e)
        pprint(a)
    else:
        pprint(mturk.list_assignments_for_hit(
            HITId=hit_id
        ).get('Assignments', []))

def approve_assignment(assignment_id):
    mturk.approve_assignment(
        AssignmentId=assignment_id,
        OverrideRejection=True
    )

def reject_assignment(assignment_id, reason):
    mturk.reject_assignment(
        AssignmentId=assignment_id,
        RequesterFeedback=reason
    )

def create_qualification(step):
    if step == 'step01' or step == 'step02':
        try:
            questions = open(file='csgame/hitData/qualification/testP3.xml', mode='r').read()
            answers = open(file='csgame/hitData/qualification/ansP3.xml', mode='r').read()
        except:
            print()
            print("----------------------")
            print('Error: no file found!')
            exit(1)
        qual_resp = mturk.create_qualification_type(
            Name = 'English comprehension writing test',
            Keywords = 'test, qualifcation, English writing skills',
            Description = "This is a test consists of 10 questions to decide your level of your english comprehension in writing, you need to get at least 6 correct to be qualified",
            QualificationTypeStatus = 'Active',
            Test=questions,
            AnswerKey=answers,
            TestDurationInSeconds=300
        )
    else:
        try:
            questions = open(file='csgame/hitData/qualification/testP3.xml', mode='r').read()
            answers = open(file='csgame/hitData/qualification/ansP3.xml', mode='r').read()
        except:
            print()
            print("----------------------")
            print('Error: no file found!')
            exit(1)
        qual_resp = mturk.create_qualification_type(
            Name = 'English comprehension reading test',
            Keywords = 'test, qualifcation, English reading skills',
            Description = "This is a test consists of 10 questions to decide your level of your english comprehension in writing, you need to get at least 6 correct to be qualified",
            QualificationTypeStatus = 'Active',
            Test=questions,
            AnswerKey=answers,
            TestDurationInSeconds=300
        )
    print(qual_resp['QualificationType']['QualificationTypeId'])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(metavar='subcommands', dest='command')
    stepsArg = dict(type=str, choices=['step01', 'step02', 'step03'], metavar='step',
                     help='Choose step01, step02, or step03.')

    cparser = subparsers.add_parser('create', help='create hits for specfic step with', aliases=['c'])
    cparser.add_argument('step', **stepsArg)
    cparser.add_argument('number', type=int, default=1, help="The number of the HITS to generate each round")

    dparser = subparsers.add_parser('delete', help='delete hits for specfic step with', aliases=['d'])
    dparser.add_argument('step', **stepsArg)

    pparser = subparsers.add_parser('print', help='print hit or assignment status', aliases=['p'])
    pparser.add_argument('-a', '--assignment', type=str, metavar='assignment', default='all', nargs='?', help='HIT id to show assignments for.')

    aparser = subparsers.add_parser('approve', help='approve the assignment', aliases=['a'])
    aparser.add_argument('assignment', type=str, metavar='assignment')

    rparser = subparsers.add_parser('reject', help='reject the assignment', aliases=['r'])
    rparser.add_argument('assignment', type=str, metavar='assignment')
    rparser.add_argument('reason', type=str, metavar='reason')

    # a parser that will be only needed once for create a qualificatio for each of the 3 steps
    qparser = subparsers.add_parser('qualify', help='create a qualification type for different 3 steps', aliases=['q'])
    qparser.add_argument('step', **stepsArg)

    options = parser.parse_args()

    # Hello world for mturk boto api
    print("I have $" + mturk.get_account_balance()['AvailableBalance'] + " in my account")
    if options.command in ('create', 'c'):
        create_hit(options.step, options.number)
    elif options.command in ('delete', 'd'):
        delete_hit(options.step)
    elif options.command in ('print', 'p'):
        hitId = options.assignment
        if hitId:
            print_assignment(hitId)
        else:
            print_hit()
    elif options.command in ('approve', 'a'):
        approve_assignment(options.assignment)
    elif options.command in ('reject', 'r'):
        reject_assignment(options.assignment, options.reason)
    elif options.command in ('qualify', 'q'):
        create_qualification(options.step)
    else:
        sys.exit(2)
