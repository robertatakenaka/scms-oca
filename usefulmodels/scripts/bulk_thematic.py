import os
import csv
from usefulmodels import models
from django.contrib.auth import get_user_model

User = get_user_model()

# This script add bulk of actions
# Consider that existe a user with id=1

SEPARATOR = ';'


def run(*args):
    user_id = 1

    # Delete all acitions
    models.ThematicArea.objects.all().delete()

    # User
    if args:
        user_id = args[0]

    creator = User.objects.get(id=user_id)
    with open(os.path.dirname(os.path.realpath(__file__)) + "/../fixtures/thematic_areas.csv", 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for line in reader:
            models.ThematicArea(
                level0=line['Nível 0'],
                level1=line['Nível 1'],
                level2=line['Nível 2'],
                creator=creator,
            ).save()
