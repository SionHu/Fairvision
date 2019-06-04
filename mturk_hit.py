# impoer django settings module to make this script work separately
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "csgame.settings")
import django
django.setup()

from django.conf import settings
mturk = settings.MTURK
#number of rounds that will be hard coded for other test
roundsnum = settings.NUMROUNDS
import sys
from sys import argv
import getopt

'''
create hits assignments with phase01a, phase01b and available rounds number
create hits assigmments with phase03 only with MaxAssignments defined by us.(Like 50?)
input: phase round number
output: HITID and HIITGroupID for preview link
'''
def create_hit(phase):
    question = open(file='hitp1.xml', mode='r').read()
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
            #delete_hit(phase)
        elif opt == '-p':
            print_hit()
