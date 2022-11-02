from django.db.models import Q

from scholarly_articles import models as article_models
from institution import models as institution_models


def load_official_name():
    for official in institution_models.Institution.objects.filter(
            source='MEC').iterator():
        for aff in article_models.Affiliations.objects.filter(
                Q(official__isnull=True) | Q(country__isnull=True),
                name__icontains=official.name).iterator():
            if not aff.official:
                aff.official = official
            if not aff.country:
                aff.country = official.location.country
            aff.save()


def run():
    load_official_name()
