# impoer django settings module to make this script work separately
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "csgame.settings")
import django
django.setup()

from django.conf import settings
mturk = settings.MTURK
#number of rounds that will be hard coded for other test
roundsnum = settings.NUMROUNDS

# getting arguments and phases
import sys
from sys import argv
import getopt

from datetime import datetime

'''
create hits assignments with phase01a, phase01b and available rounds number
create hits assigmments with phase03 only with MaxAssignments defined by us.(Like 50?)
input: phase round number
output: HITID and HIITGroupID for preview link
'''
def create_hit(phase):
    # phase 01a
    if(phase == 'phase01a'):
        try:
            question = open(file='hitp1.xml', mode='r').read()
        except:
            print()
            print("----------------------")
            print('Error: no file found!')
            exit(1)
        # create new hit
        new_hit = mturk.create_hit(
            Title="test for cds game redirect",
            Description="This is just a test for cds",
            Keywords='image, tagging',
            Reward = '0.15',
            MaxAssignments=10,
            LifetimeInSeconds=172800,
            AssignmentDurationInSeconds=6000,
            AutoApprovalDelayInSeconds=14400,
            Question=question,
        )
    # phase 01b
    elif(phase == 'phase01b'):
        try:
            open(file='hitp1b.xml', mode='r').read()
        except:
            print()
            print("----------------------")
            print('Error: no file found!')
            exit(1)
    else:
        try:
            open(file='hitp3.xml', mode='r').read()
        except:
            print()
            print("----------------------")
            print('Error: no file found!')
            exit(1)

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
    # Delete all HITs for now
    for item in mturk.list_hits()['HITs']:
        hit_id=item['HITId']
        print('HITId:', hit_id)

        # GET the HIT status
        status = mturk.get_hit(HITId=hit_id)['HIT']['HITStatus']
        print('HITStatus: ', status)
        # If HIT is active then set it to expire immediately
        if status=='Assignable':
            response = mturk.update_expiration_for_hit(
                HITId=hit_id,
                ExpireAt=datetime(2015, 1, 1)
            )
        description = mturk.get_hit(HITId=hit_id)['HIT']['Description']
        if description == 'This is just a test for cds':
            print("I found for phase1a")
        # Delete the HIT
        try:
            mturk.delete_hit(HITId=hit_id)
        except:
            print('Not deleted')
        else:
            print('Deleted')


if __name__ == "__main__":
    # create_hit()
    try:
        opts, args = getopt.getopt(argv[1:],"hpc:d:", ["create_phase=", "delete_phase="])
    except getopt.GetoptError:
      print()
      print("-----------------------------------------")
      print ('refer to commands with -h: \'python create_hit.py -h\'')
      sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print()
            print("-----------------------------------------")
            print('    create hits for specfic phase with:')
            print('python mturk_hit.py -c <create_phase>')
            print('    or delete hits for specfic phase with:')
            print('python mturk_hit.py -d <delete_phase>')
            print('    or print hit status with:')
            print('python mturk_hit.py -p')
            sys.exit()
        elif opt in ("-c", "--create_phase"):
            phase=arg.strip()
            if phase != 'phase01a' and phase != 'phase01b' and phase != 'phase03':
                print()
                print("-----------------------------------------")
                print("Error: Please use correct phase: phase01a or phase01b or phase03")
                sys.exit(2)
            create_hit(phase)
        elif opt in ("-d", "--delete_phase"):
            phase=arg.strip()
            if phase != 'phase01a' and phase != 'phase01b' and phase != 'phase03':
                print()
                print("-----------------------------------------")
                print("Error: Please use correct phase: phase01a or phase01b or phase03")
                sys.exit(2)
            delete_hit(phase)
        elif opt == '-p':
            print_hit()
