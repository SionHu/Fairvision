#!/usr/bin/env python
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

print("You are attempting to clear the database. This can be dangerous.")
print("You may want to make a savepoint first. Use the command below:")
print("\n    [heroku run] ./manage.py dumpdata users > savepoint.json\n")
print("To reload the savepoint, use the command below:")
print("\n    [heroku run] ./manage.py loaddata --format=json - < savepoint.json\n")


if strtobool(input("Are you REALLY sure you want to delete the data? ")):
    cursor = connection.cursor()
    models = ",".join(model._meta.db_table for model in MODELS)
    # Reset the models to IDENTITY
    cursor.execute("TRUNCATE {} RESTART IDENTITY CASCADE;".format(models))
    print("Success.")
