#!/usr/bin/env python

# impoer django settings module to make this script work separately
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "csgame.settings")
from pprint import pprint

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
    # phase 01a
    for i in range(number):
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
                Title="Image Labeling With Text",
                Description="Generating questions and answers and verifying question given a shown image",
                Keywords='image, tagging, machine learning, text generation',
                Reward = '0.15',
                MaxAssignments=1,
                LifetimeInSeconds=60*60*24*10,
                AssignmentDurationInSeconds=35*60,
                AutoApprovalDelayInSeconds=60*60*24*3,
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
                Title="Knowledge Answer With Image",
                Description="Given 4 images of same single object and list of questions, answer all the questions that you think are meaningful",
                Keywords='image, tagging',
                Reward = '0.15',
                MaxAssignments=1,
                LifetimeInSeconds=60*60*24*10,
                AssignmentDurationInSeconds=35*60,
                AutoApprovalDelayInSeconds=60*60*24*3,
                Question=question,
            )
        else:
            # phase 03
            try:
                question = open(file='hitExteranl/hitp3.xml', mode='r').read()
            except:
                print()
                print("----------------------")
                print('Error: no file found!')
                exit(1)
            # create new hit
            new_hit = mturk.create_hit(
                Title="Binary Selection Question",
                Description="Vote YES or NO for question provided based on common sense",
                Keywords='binary tagging, text verification, computer vision, machine learning',
                Reward = '0.05',
                MaxAssignments=1,
                LifetimeInSeconds=60*60*24*10,
                AssignmentDurationInSeconds=600,
                AutoApprovalDelayInSeconds=60*60*24*3,
                Question=question,
            )

        # some print function for reference
        print(f"https://worker.mturk.com/mturk/preview?groupId={new_hit['HIT']['HITGroupId']}")
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
        if phase == 'phase01a' and description == 'Generating questions and answers and verifying question given a shown image':
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
        elif phase == 'phase01b' and description == 'Given 4 images of same single object and list of questions, answer all the questions that you think are meaningful':

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
        elif phase == 'phase03' and description == 'Vote YES or NO for question provided based on common sense':
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
    pparser.add_argument('-a', '--assignment', type=str, metavar='assignment', default='all', nargs='?', help='HIT id to show assignments for.')

    aparser = subparsers.add_parser('approve', help='approve the assignment', aliases=['a'])
    aparser.add_argument('assignment', type=str, metavar='assignment')

    rparser = subparsers.add_parser('reject', help='reject the assignment', aliases=['r'])
    rparser.add_argument('assignment', type=str, metavar='assignment')
    rparser.add_argument('reason', type=str, metavar='reason')


    options = parser.parse_args()

    # Hello world for mturk boto api
    print("I have $" + mturk.get_account_balance()['AvailableBalance'] + " in my account")
    if options.command in ('create', 'c'):
        create_hit(options.phase, options.number)
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
