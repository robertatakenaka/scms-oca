import csv
from datetime import datetime

from django.utils.translation import gettext as _

from institution.models import Institution
from usefulmodels.models import Action, Practice, ThematicArea

from .models import EducationDirectory


def load_data_from_file(file_path, user):
    ACTION = 'educação / capacitação'
    # EducationDirectoryFile.objects.all().delete()

    try:
        with open(file_path, 'r') as csvfile:
            data = csv.DictReader(csvfile, delimiter=";")

            for line, row in enumerate(data):
                # Action
                if row['Action'] != ACTION and row['Action'] in ACTION:
                    row['Action'] = ACTION

                if row['Action'] != ACTION:
                    raise ValueError(
                        _("Importing %s | Invalid value in %s | line: %s | %s") %
                        (ACTION, "Action", str(line + 2), row))
                    continue

                try:
                    ed = EducationDirectory.objects.get(link=row['Link'], title=row['Title'])
                except EducationDirectory.DoesNotExist:
                    ed = EducationDirectory()
                except EducationDirectory.MultipleObjectsReturned:
                    try:
                        EducationDirectory.objects.filter(link=row['Link'], title=row['Title']).delete()
                        ed = EducationDirectory()
                    except Exception as e:
                        raise ValueError(
                            _("Importing %s | Invalid value in %s | line: %s | %s") %
                            (e, "row", str(line + 2), row))
                        continue

                # Action
                try:
                    ed.action = Action.objects.get(name=row['Action'])
                except Action.DoesNotExist:
                    ed.action = Action(name=row['Action'], creator=user)
                    ed.action.save()

                # Practice
                try:
                    ed.practice = Practice.objects.get(name=row['Practice'])
                except Practice.DoesNotExist:
                    ed.practice = Practice(name=row['Practice'], creator=user)
                    ed.practice.save()

                ed.title = row['Title']
                ed.link = row['Link']
                ed.description = row['Description']
                if row['Start Date']:
                    ed.start_date = datetime.strptime(row['Start Date'], '%d/%m/%Y')
                if row['End Date']:
                    ed.end_date = datetime.strptime(row['End Date'], '%d/%m/%Y')
                if row['Start Time']:
                    ed.start_time = row['Start Time']
                if row['End Time']:
                    ed.end_time = row['End Time']
                ed.creator = user
                ed.save()

                # Institution
                inst_name = row['Institution Name'].strip()
                if inst_name:
                    inst_country = row['Institution Country'].strip()
                    inst_state = row['Institution State'].strip()
                    inst_city = row['Institution City'].strip()

                    institution = Institution.get_or_create(inst_name, inst_country, inst_state, inst_city, user)
                    ed.institutions.add(institution)

                # Thematic Area
                level0 = row['Thematic Area Level0'].strip()
                if level0:
                    level1 = row['Thematic Area Level1'].strip()
                    level2 = row['Thematic Area Level2'].strip()
                    the_area = ThematicArea.get_or_create(level0, level1, level2, user)

                    ed.thematic_areas.add(the_area)

                # Keywords
                if row['Keywords']:
                    for key in row['Keywords'].split('|'):
                        ed.keywords.add(key)

                if row['Classification']:
                    ed.classification = row['Classification']

                if row['Source']:
                    ed.source = row['Source']

                ed.save()
    except Exception as ex:
        raise ValueError(
            _("Import error: %s, Line: %s") % (ex, str(line + 2)))
    else:
        return True
