import csv
import os

from django.contrib.auth import get_user_model

from institution import models
from location.models import Location
from usefulmodels.models import State

User = get_user_model()

def load_or_up_date(inst, row, creator):
    inst.name = row['Name']
    inst.institution_type = row['Institution Type']
    inst.acronym = row['Acronym']
    inst.source = 'MEC'
    inst.level_1 = row['Level_1']
    inst.level_2 = row['Level_2']
    inst.level_3 = row['Level_3']
    state_name = State.get_or_create(acronym=row['State Acronym'], user=creator).name
    inst.location = Location.get_or_create(user=creator,
                                           location_country="Brasil",
                                           location_state=state_name,
                                           location_city=None)
    inst.creator = creator


def load_official_institution(creator, row, line):
    try:
        for inst in models.Institution.objects.filter(name=row['Name'], acronym=row['Acronym']).iterator():
            load_or_up_date(inst, row, creator)
            inst.save()

        if not models.Institution.objects.filter(name=row['Name'], acronym=row['Acronym']).exists():
            inst = models.Institution()
            load_or_up_date(inst, row, creator)
            inst.save()

    except Exception as ex:
        print("Import error: %s, Line: %s" % (ex, str(line + 2)))
    else:
        print("File imported successfully!")


def run(*args):
    user_id = args[0] if args else 1

    user = User.objects.get(id=user_id)

    with open(os.path.dirname(os.path.realpath(__file__)) + "/../fixtures/institutions.csv", 'r') as csvfile:
        data = csv.DictReader(csvfile, delimiter=";")

        for line, row in enumerate(data):
            load_official_institution(creator=user, row=row, line=line)