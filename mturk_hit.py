# impoer django settings module to make this script work separately
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "csgame.settings")
import django
django.setup()

from django.conf import settings
from csgame.storage_backends import mturk
#number of rounds that will be hard coded for other test
roundsnum = settings.NUMROUNDS
import sys
import argparse

'''
create hits assignments with phase01a, phase01b and available rounds number
create hits assigmments with phase03 only with MaxAssignments defined by us.(Like 50?)
input: phase round number
output: HITID and HIITGroupID for preview link
'''
def create_hit(phase):
    question = open(file='hitp1.xml', mode='r').read()
    new_hit = mturk.create_hit(
        Title="test for cds game well",
        Description="This is just a test for cds",
        Keywords='image, tagging',
        Reward = '0.15',
        MaxAssignments=10,
        LifetimeInSeconds=172800,
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
input argument: phase number
output print: HIT and Some title
'''
def print_hit():
    print(mturk.list_hits()['HITs'])

def delete_hit(phase):
    # Delete HITs
    for item in mturk.list_hits()['HITs']:
        hit_id=item['HITId']
        print('HITId:', hit_id)
    print(mturk.list_hits()['HITs'])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--images', type=str, default=None, help="file containing ID,URL pairs")
    parser.add_argument('--pretend', action='store_true', help="show what would be done; don't do it")

    subparsers = parser.add_subparsers(metavar='subcommands', dest='command')
    phasesArg = dict(type=str, choices=['phase01a', 'phase01b', 'phase03'], metavar='phase',
                     help='Choose phase01a, phase01b, or phase03.')

    cparser = subparsers.add_parser('create', help='create hits for specfic phase with', aliases=['c'])
    cparser.add_argument('phase', **phasesArg)

    dparser = subparsers.add_parser('delete', help='delete hits for specfic phase with', aliases=['d'])
    dparser.add_argument('phase', **phasesArg)

    subparsers.add_parser('print', help='print hit status', aliases=['p'])
    options = parser.parse_args()


    print("I have $" + mturk.get_account_balance()['AvailableBalance'] + " in my account")
    if options.command in ('create', 'c'):
        create_hit(options.phase)
    elif options.command in ('delete', 'd'):
        delete_hit(options.phase)
    elif options.command in ('print', 'p'):
        print_hit()
    else:
        sys.exit(2)
