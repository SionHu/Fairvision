#!/usr/bin/env python
# impoer django settings module to make this script work separately
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "csgame.settings")
import pprint

from django.conf import settings
from csgame.storage_backends import mturk
#number of rounds that will be hard coded for other test
roundsnum = settings.NUMROUNDS

# getting arguments and phases
import sys
import argparse

from datetime import datetime

'''
create hits assignments with phase01a, phase01b and available rounds number
create hits assigmments with phase03 only with MaxAssignments defined by us.(Like 50?)
input: phase round number
output: HITID and HIITGroupID for preview link
'''
def create_hit(phase, number):
    for i in range(number):
        # phase 01a
        if(phase == 'phase01a'):
            try:
                question = open(file='hitExternal/hitp1.xml', mode='r').read()
            except:
                print()
                print("----------------------")
                print('Error: no file found!')
                exit(1)
            # create new hit
            new_hit = mturk.create_hit(
                Title="Image QA phase01a",
                Description="The phase01a for generating the QA pairs from the given image about a common single object from machine learning image classification dataset",
                Keywords='image, tagging, machine learning, text generation',
                Reward = '0.25',
                MaxAssignments=10,
                LifetimeInSeconds=172800,
                AssignmentDurationInSeconds=6000,
                AutoApprovalDelayInSeconds=14400,
                Question=question,
            )
        # phase 01b
        elif(phase == 'phase01b'):
            try:
                question = open(file='hitExternal/hitp1b.xml', mode='r').read()
            except:
                print()
                print("----------------------")
                print('Error: no file found!')
                exit(1)
            # create new hit
            new_hit = mturk.create_hit(
                Title="Image QA phase01b",
                Description="The phase03 for crowdsourcing game, given an image of single object from ML image dataset, answer the questions provided",
                Keywords='image, tagging',
                Reward = '0.25',
                MaxAssignments=1,
                LifetimeInSeconds=7200,
                AssignmentDurationInSeconds=6000,
                AutoApprovalDelayInSeconds=14400,
                Question=question,
            )
        else:
            # phase 03
            try:
                question = open(file='hitExternal/hitp3.xml', mode='r').read()
            except:
                print()
                print("----------------------")
                print('Error: no file hitp3.xml found!')
                exit(1)
            # create new hit
            new_hit = mturk.create_hit(
                Title="Vote phase03",
                Description="The phase03 for crowdsourcing game, vote YES or NO for question provided based on common sense",
                Keywords='binary tagging, text verification, computer vision, machine learning',
                Reward = '0.25',
                MaxAssignments=11,
                LifetimeInSeconds=7200,
                AssignmentDurationInSeconds=6000,
                AutoApprovalDelayInSeconds=14400,
                Question=question,
            )

        # some print function for reference
        print(new_hit['HIT']['HITGroupId'])
        print("https://workersandbox.mturk.com/mturk/preview?groupId=", new_hit['HIT']['HITGroupId'])
        print("HITID = " + new_hit['HIT']['HITId'] + " (Use to Get Results)")

'''
check available hit
input argument: N/A
output print: HIT and Some title
'''
def print_hit():
    pprint.pprint(mturk.list_hits()['HITs'])

'''
delete_hit for different
input argument: phase number
output print: delete HIT ID, Status and delete message: success or fail
Note: This should only been done for sandbox(development) or between the phase gap
'''
def delete_hit(phase):
    # Delete all HITs for now
    for item in mturk.list_hits()['HITs']:
        hit_id=item['HITId']
        print('HITId:', hit_id)

        # GET the HIT status
        status = mturk.get_hit(HITId=hit_id)['HIT']['HITStatus']
        print('HITStatus: ', status)
        description = mturk.get_hit(HITId=hit_id)['HIT']['Description']

        # delete phase01a
        if phase == 'phase01a' and description == 'The phase01a for generating the QA pairs from the given image about a common single object from machine learning image classification dataset':
            # If HIT is active then set it to expire immediately
            if status=='Assignable':
                response = mturk.update_expiration_for_hit(
                    HITId=hit_id,
                    ExpireAt=datetime(2015, 1, 1)
                )

            print("I found for phase1a")
            # Delete the HIT
            try:
                mturk.delete_hit(HITId=hit_id)
            except:
                print('Not deleted')
            else:
                print('Deleted')
        elif phase == 'phase01b' and description == 'The phase01b for crowdsourcing game, given an image of single object from ML image dataset, answer the questions provided':

            # If HIT is active then set it to expire immediately
            if status=='Assignable':
                response = mturk.update_expiration_for_hit(
                    HITId=hit_id,
                    ExpireAt=datetime(2015, 1, 1)
                )

            print("I found for phase1a")
            # Delete the HIT
            try:
                mturk.delete_hit(HITId=hit_id)
            except:
                print('Not deleted')
            else:
                print('Deleted')
        elif phase == 'phase03' and description == 'The phase03 for crowdsourcing game, given an image of single object from ML image dataset, answer the questions provided':
            # If HIT is active then set it to expire immediately
            if status=='Assignable':
                response = mturk.update_expiration_for_hit(
                    HITId=hit_id,
                    ExpireAt=datetime(2015, 1, 1)
                )

            print("I found for phase1a")
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
    pprint.pprint(mturk.list_assignments_for_hit(
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(metavar='subcommands', dest='command')
    phasesArg = dict(type=str, choices=['phase01a', 'phase01b', 'phase03'], metavar='phase',
                     help='Choose phase01a, phase01b, or phase03.')

    cparser = subparsers.add_parser('create', help='create hits for specfic phase with', aliases=['c'])
    cparser.add_argument('phase', **phasesArg)
    cparser.add_argument('number', type=int, default=1, help="The number of the HITS to generate each round")

    dparser = subparsers.add_parser('delete', help='delete hits for specfic phase with', aliases=['d'])
    dparser.add_argument('phase', **phasesArg)

    pparser = subparsers.add_parser('print', help='print hit or assignment status', aliases=['p'])
    pparser.add_argument('--assignment', type=str, metavar='assignment', help='HIT id to show assignments for.')

    aparser = subparsers.add_parser('approve', help='approve the assignment', aliases=['a'])
    aparser.add_argument('assignment', type=str, metavar='assignment')

    rparser = subparsers.add_parser('reject', help='reject the assignment', aliases=['r'])
    rparser.add_argument('assignment', type=str, metavar='assignment')

    options = parser.parse_args()

    # Hello world for mturk boto app

    if options.command in ('create', 'c'):
        create_hit(options.phase, options.number)
    # elif options.command in ('create')
    elif options.command in ('delete', 'd'):
        delete_hit(options.phase)
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
    else:
        sys.exit(2)
