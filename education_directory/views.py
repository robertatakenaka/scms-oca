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

from .models import EducationDirectory, EducationDirectoryFile


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
        file_upload = get_object_or_404(EducationDirectoryFile, pk=file_id)

    if request.method == 'GET':
        try:
            upload_path = file_upload.attachment.file.path
            cols = chkcsv.read_format_specs(
                os.path.dirname(os.path.abspath(__file__)) + "/chkcsvfmt.fmt", True, False)
            errorlist = chkcsv.check_csv_file(upload_path, cols, True, True, True, False)
            if errorlist:
                raise Exception(_("Validation error"))
            else:
                file_upload.is_valid = True
                fp = open(upload_path)
                file_upload.line_count = len(fp.readlines())
                file_upload.save()
        except Exception as ex:
            messages.error(request, _("Validation error: %s") % errorlist)
        else:
            messages.success(request, _("File successfully validated!"))

    return redirect(request.META.get('HTTP_REFERER'))


def import_file(request):
    """
    This view function import the data from a CSV file.

    Something like this:

        Title,Link,Description
        FAPESP,http://www.fapesp.com.br,primary

    TODO: This function must be a task.
    """
    file_id = request.GET.get("file_id", None)

    if file_id:
        file_upload = get_object_or_404(EducationDirectoryFile, pk=file_id)

    file_path = file_upload.attachment.file.path

    ACTION_NAME = 'educação / capacitação'
    # EducationDirectoryFile.objects.all().delete()

    try:
        with open(file_path, 'r') as csvfile:
            data = csv.DictReader(csvfile, delimiter=";")

            for line, row in enumerate(data):

                for k, v in row.items():
                    row[k] = v.strip()
                # Action
                if row['Action'] != ACTION_NAME and row['Action'] in ACTION_NAME:
                    row['Action'] = ACTION_NAME

                if row['Action'] != ACTION_NAME:
                    messages.error(
                        request,
                        _("Importing %s | Invalid value in %s | line: %s | %s") %
                        (ACTION_NAME, "Action", str(line + 2), row))
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
                        messages.error(
                            request,
                            _("Importing %s | Invalid value in %s | line: %s | %s") %
                            (e, "row", str(line + 2), row))
                        continue

                # Action
                try:
                    ed.action = Action.objects.get(name__icontains=row['Action'])
                except Action.DoesNotExist:
                    ed.action = Action(name=row['Action'], creator=request.user)
                    ed.action.save()

                # Practice
                try:
                    ed.practice = Practice.objects.get(name__icontains=row['Practice'])
                except Practice.DoesNotExist:
                    ed.practice = Practice(name=row['Practice'], creator=request.user)
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
                ed.creator = request.user
                ed.save()

                # Institution
                inst_name = row['Institution Name'].strip()
                if inst_name:
                    inst_country = row['Institution Country'].strip()
                    inst_state = row['Institution State'].strip()
                    inst_city = row['Institution City'].strip()

                    institution = Institution.get_or_create(inst_name, inst_country, inst_state, inst_city, request.user)
                    ed.institutions.add(institution)

                # Thematic Area
                level0 = row['Thematic Area Level0'].strip()
                if level0:
                    level1 = row['Thematic Area Level1'].strip()
                    level2 = row['Thematic Area Level2'].strip()
                    the_area = ThematicArea.get_or_create(level0, level1, level2, request.user)

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
        messages.error(request, _("Import error: %s, Line: %s") % (ex, str(line + 2)))
    else:
       messages.success(request, _("File imported successfully!"))

    return redirect(request.META.get('HTTP_REFERER'))


def download_sample(request):
    """
    This view function a CSV sample for model EducationDirectoryFile.
    """
    file_path = os.path.dirname(os.path.abspath(__file__)) + "/example_education.csv"
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="text/csv")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404


    start_time = models.TimeField(_("Start Time"), max_length=255,
                                  null=True, blank=True)
    end_time = models.TimeField(_("End Time"), max_length=255,
                                  null=True, blank=True)
