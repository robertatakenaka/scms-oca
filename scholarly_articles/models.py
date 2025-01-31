from django.db import models
from django.utils.translation import gettext as _

from wagtail.admin.edit_handlers import FieldPanel

from . import choices


class ScholarlyArticles(models.Model):
    doi = models.CharField("DOI", max_length=255, null=False, blank=False)
    doi_url = models.URLField("DOI URL", max_length=255, null=True, blank=True)
    genre = models.CharField("Resource Type", max_length=255, choices=choices.TYPE_OF_RESOURCE, null=False, blank=False)
    is_oa = models.BooleanField("Opens Access", max_length=255, null=True, blank=True)
    journal_is_in_doaj = models.BooleanField("DOAJ", max_length=255, null=True, blank=True)
    journal_issns = models.CharField("ISSN's", max_length=255, null=False, blank=False)
    journal_issn_l = models.CharField("ISSN-L", max_length=255, null=False, blank=False)
    journal_name = models.CharField("Journal Name", max_length=255, null=True, blank=True)
    published_date = models.DateTimeField("Published Date", max_length=255, null=True, blank=True)
    publisher = models.CharField("Publisher", max_length=255, null=True, blank=True)
    title = models.CharField("Title", max_length=255, null=True, blank=True)
    article_json = models.JSONField("JSON File", null=True, blank=True)

    panels = [
        FieldPanel('doi'),
        FieldPanel('doi_url'),
        FieldPanel('genre'),
        FieldPanel('is_oa'),
        FieldPanel('journal_is_in_doaj'),
        FieldPanel('journal_issns'),
        FieldPanel('journal_issn_l'),
        FieldPanel('journal_name'),
        FieldPanel('published_date'),
        FieldPanel('publisher'),
        FieldPanel('title'),
        FieldPanel('article_json'),
    ]


class Contributors(models.Model):
    doi = models.CharField("DOI", max_length=255, null=False, blank=False)
    doi_url = models.URLField("DOI URL", max_length=255, null=True, blank=True)
    family = models.CharField("Family", max_length=255, null=False, blank=False)
    given = models.CharField("Given", max_length=255, null=False, blank=False)
    orcid = models.URLField("ORCID", max_length=255, null=False, blank=False)
    authenticated_orcid = models.BooleanField("Authenticated", max_length=255, null=False, blank=False)
    affiliation = models.CharField("Affiliation", max_length=255, null=False, blank=False)

    panels = [
        FieldPanel('doi'),
        FieldPanel('doi_url'),
        FieldPanel('family'),
        FieldPanel('given'),
        FieldPanel('orcid'),
        FieldPanel('authenticated_orcid'),
        FieldPanel('affiliation'),
    ]
