'''
Usage: script for using the nlp server to
Data input: list contains of Question with text + id; Corresponding Answers for each question with text + id;
Output: ID that get merged for answers
'''

# impoer django settings module to make this script work separately
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "csgame.settings")
import django
django.setup()


def phase02:
