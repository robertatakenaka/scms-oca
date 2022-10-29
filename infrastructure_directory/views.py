import csv
import os

from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext as _
from wagtail.admin import messages

from core.libs import chkcsv
from infrastructure_directory.search_indexes import InfraStructureIndex
from institution.models import Institution
from usefulmodels.models import Action, Practice, ThematicArea

from .models import InfrastructureDirectory, InfrastructureDirectoryFile


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
        file_upload = get_object_or_404(InfrastructureDirectoryFile, pk=file_id)

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
        file_upload = get_object_or_404(InfrastructureDirectoryFile, pk=file_id)

    file_path = file_upload.attachment.file.path

    ACTION_NAME = 'infraestrutura'

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
                    isd = InfrastructureDirectory.objects.get(link=row['Link'], title=row['Title'])
                except InfrastructureDirectory.DoesNotExist:
                    isd = InfrastructureDirectory()
                except InfrastructureDirectory.MultipleObjectsReturned:
                    try:
                        InfrastructureDirectory.objects.filter(link=row['Link'], title=row['Title']).delete()
                        isd = InfrastructureDirectory()
                    except Exception as e:
                        messages.error(
                            request,
                            _("Importing %s | Invalid value in %s | line: %s | %s") %
                            (e, "row", str(line + 2), row))
                        continue

                # Action
                try:
                    isd.action = Action.objects.get(name__icontains=row['Action'])
                except Action.DoesNotExist:
                    isd.action = Action(name=row['Action'], creator=request.user)
                    isd.action.save()

                # Practice
                try:
                    isd.practice = Practice.objects.get(name__icontains=row['Practice'])
                except Practice.DoesNotExist:
                    isd.practice = Practice(name=row['Practice'], creator=request.user)
                    isd.practice.save()

                isd.title = row['Title']
                isd.link = row['Link']
                isd.description = row['Description']

                isd.creator = request.user
                isd.save()

                # Institution
                inst_name = row['Institution Name']
                if inst_name:
                    inst_country = row['Institution Country']
                    inst_state = row['Institution State']
                    inst_city = row['Institution City']

                    institution = Institution.get_or_create(inst_name, inst_country,
                                                            inst_state, inst_city, request.user)
                    isd.institutions.add(institution)

                # Thematic Area
                level0 = row['Thematic Area Level0'].strip()
                if level0:
                    level1 = row['Thematic Area Level1'].strip()
                    level2 = row['Thematic Area Level2'].strip()
                    the_area = ThematicArea.get_or_create(level0, level1, level2, request.user)

                    isd.thematic_areas.add(the_area)

                # Keywords
                if row['Keywords']:
                    for key in row['Keywords'].split('|'):
                        isd.keywords.add(key)

                if row['Classification']:
                    isd.classification = row['Classification']

                if row['Source']:
                    isd.source = row['Source']

                isd.save()

    except Exception as ex:
        messages.error(request, _("Import error: %s, Line: %s") % (ex, str(line + 2)))
    else:
        messages.success(request, _("File imported successfully!"))

    return redirect(request.META.get('HTTP_REFERER'))


def download_sample(request):
    """
    This view function a CSV sample for model InfraestructureDirectoryFile.
    """
    file_path = os.path.dirname(os.path.abspath(__file__)) + "/example_infra.csv"
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="text/csv")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404
