import csv
import os
from datetime import datetime

from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext as _
from wagtail.admin import messages

from core.libs import chkcsv
from institution.models import Institution
from usefulmodels.models import Action, Practice, ThematicArea

from .models import EventDirectory, EventDirectoryFile


def validate(request):
    """
    This view function validade a csv file based on a pre definition os the fmt
    file.

    The check_csv_file function check that all of the required columns and data
    are present in the CSV file, and that the data conform to the appropriate
    type and other specifications, when it is not valid return a list with the
    errors.
    """
    errorlist = []
    file_id = request.GET.get("file_id", None)

    if file_id:
        file_upload = get_object_or_404(EventDirectoryFile, pk=file_id)

    if request.method == 'GET':
        try:
            upload_path = file_upload.attachment.file.path
            cols = chkcsv.read_format_specs(
                os.path.dirname(os.path.abspath(__file__)) + "/chkcsvfmt.fmt", True, False)
            errorlist = chkcsv.check_csv_file(upload_path, cols, True, True, True, False)
            if errorlist:
                raise Exception(_("Valication error"))
            else:
                file_upload.is_valid = True
                fp = open(upload_path)
                file_upload.line_count = len(fp.readlines())
                file_upload.save()
        except Exception as ex:
            messages.error(request, _("Valication error: %s") % errorlist)
        else:
            messages.success(request, _("File successfully validated!"))

    return redirect(request.META.get('HTTP_REFERER'))


def import_file(request):
    """
    This view function import the data from a CSV file.

    Something like this:

        Event,Link,Description,Organization
        Seminário X,http://www.sem.com.br,Seminário XPTO,SciELO

    TODO: This function must be a task.
    """
    file_id = request.GET.get("file_id", None)

    if file_id:
        file_upload = get_object_or_404(EventDirectoryFile, pk=file_id)

    file_path = file_upload.attachment.file.path

    # try:
    ACTION_NAME = 'disseminação'
    # EventDirectory.objects.all().delete()

    with open(file_path, 'r') as csvfile:
        data = csv.DictReader(csvfile, delimiter=";")

        for line, row in enumerate(data):

            # Action
            if row['Action'] == 'eventos':
                row['Action'] = ACTION_NAME

            if row['Action'] != ACTION_NAME:
                messages.error(
                    request,
                    _("Importing %s | Invalid value in %s | line: %s | %s") %
                    (ACTION_NAME, "Action", str(line + 2), row))
                continue

            try:
                di = EventDirectory.objects.get(link=row['Link'], title=row['Title'])
            except EventDirectory.DoesNotExist:
                di = EventDirectory()
            except EventDirectory.MultipleObjectsReturned:
                try:
                    EventDirectory.objects.filter(link=row['Link'], title=row['Title']).delete()
                    di = EventDirectory()
                except Exception as e:
                    messages.error(
                        request,
                        _("Importing %s | Invalid value in %s | line: %s | %s") %
                        (e, "row", str(line + 2), row))
                    continue

            # Action
            try:
                di.action = Action.objects.get(name=row['Action'])
            except Action.DoesNotExist:
                di.action = Action(name=row['Action'], creator=request.user)
                di.action.save()

            # Practice
            try:
                di.practice = Practice.objects.get(name=row['Practice'])
            except Practice.DoesNotExist:
                di.practice = Practice(name=row['Practice'], creator=request.user)
                di.practice.save()

            di.title = row['Title']
            di.link = row['Link']
            di.description = row['Description']
            if row['Start Date']:
                di.start_date = datetime.strptime(row['Start Date'], '%d/%m/%Y')
            if row['End Date']:
                di.end_date = datetime.strptime(row['End Date'], '%d/%m/%Y')
            if row['Start Time']:
                di.start_time = row['Start Time']
            if row['End Time']:
                di.end_time = row['End Time']
            di.creator = request.user
            di.save()

            # Institution
            inst_name = row['Institution Name']
            if inst_name:
                inst_country = row['Institution Country']
                inst_state = row['Institution State']
                inst_city = row['Institution City']

                institution = Institution.get_or_create(inst_name, inst_country,
                                                        inst_state, inst_city, request.user)
                di.organization.add(institution)

            # Thematic Area
            level0 = row['Thematic Area Level0'].strip()
            if level0:
                level1 = row['Thematic Area Level1'].strip()
                level2 = row['Thematic Area Level2'].strip()
                the_area = ThematicArea.get_or_create(level0, level1, level2, request.user)

                di.thematic_areas.add(the_area)

            # Keywords
            if row['Keywords']:
                for key in row['Keywords'].split('|'):
                    di.keywords.add(key)

            if row['Classification']:
                di.classification = row['Classification']

            if row['Source']:
                di.source = row['Source']

            di.save()

    # except Exception as ex:
    #     messages.error(request, _("Import error: %s, Line: %s") % (ex, str(line + 2)))
    # else:
    #    messages.success(request, _("File imported successfully!"))

    return redirect(request.META.get('HTTP_REFERER'))


def download_sample(request):
    """
    This view function a CSV sample for model EventDirectoryFile.
    """
    file_path = os.path.dirname(os.path.abspath(__file__)) + "/example_event.csv"
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="text/csv")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404
