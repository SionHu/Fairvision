'''
Usage: Run to clear all of the user entered data and HIT data from the database. You have been warned.
'''

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "csgame.settings")
import django
django.setup()

from distutils.util import strtobool
from django.db import connection
from users.models import Attribute, HIT, Phase, Question

# Models that will be reset by this script. Add more if you feel they should be included.
MODELS = (Attribute, HIT, Phase, Question)

if strtobool(input("You are attempting to clear the database. Are you REALLY sure you want to do this? ")):
    cursor = connection.cursor()
    models = ",".join(model._meta.db_table for model in MODELS)
    # Reset the models to IDENTITY
    cursor.execute("TRUNCATE {} RESTART IDENTITY CASCADE;".format(models))
    print("Success.")
