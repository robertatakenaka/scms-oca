import os

from django.db import models
from django.utils.translation import gettext as _
from taggit.managers import TaggableManager
from wagtail.admin.edit_handlers import FieldPanel, HelpPanel
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtailautocomplete.edit_handlers import AutocompletePanel

from core.models import CommonControlField
from institution.models import Institution
from usefulmodels.models import ThematicArea, Practice, Action

from .forms import PolicyDirectoryFileForm, PolicyDirectoryForm

from . import choices


class PolicyDirectory(CommonControlField):

    class Meta:
        verbose_name_plural = _('Policy Directory')

        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['date']),
            models.Index(fields=['practice']),
            models.Index(fields=['action']),
            models.Index(fields=['classification']),
            models.Index(fields=['source']),
            models.Index(fields=['record_status']),
        ]

    title = models.CharField(_("Title"), max_length=255, null=False, blank=False)
    link = models.URLField(_("Link"), null=False, blank=False)
    description = models.TextField(_("Description"), max_length=1000,
                                   null=True, blank=True)
    date = models.DateField(_("Date"), max_length=255,
                                  null=True, blank=True)

    institutions = models.ManyToManyField(Institution, verbose_name=_("Institution"), blank=True)
    thematic_areas = models.ManyToManyField(ThematicArea, verbose_name=_("Thematic Area"), blank=True)

    practice = models.ForeignKey(Practice, verbose_name=_("Practice"),
                                null=True, blank=True, on_delete=models.SET_NULL)
    action = models.ForeignKey(Action, verbose_name=_("Action"), null=True, blank=True, on_delete=models.SET_NULL)

    classification = models.CharField(_("Classification"), choices=choices.classification,
                                      max_length=255, null=True, blank=True)

    keywords = TaggableManager(_("Keywords"), blank=True)

    record_status = models.CharField(_("Record status"), choices=choices.status,
                                     max_length=255, null=True, blank=True)

    source = models.CharField(_("Source"), max_length=255, null=True, blank=True)

    panels = [
        HelpPanel('Documentos de promoção, posicionamentos ou mandatos sobre Ciência Aberta elaborados e publicados por instituições brasileiras, tais como: universidades, sociedades científicas, institutos de pesquisa e agências de fomento.'),
        FieldPanel('title'),
        FieldPanel('link'),
        FieldPanel('source'),

        FieldPanel('description'),
        AutocompletePanel('institutions'),

        AutocompletePanel('thematic_areas'),
        FieldPanel('keywords'),
        FieldPanel('classification'),
        FieldPanel('practice'),

        FieldPanel('source'),
        FieldPanel('record_status'),

    ]

    def __unicode__(self):
        return u'%s' % self.title

    def __str__(self):
        return u'%s' % self.title
    base_form_class = PolicyDirectoryForm

class PolicyDirectoryFile(CommonControlField):
    class Meta:
        verbose_name_plural = _('Policy Directory Upload')

    attachment = models.ForeignKey(
        'wagtaildocs.Document',
        verbose_name=_("Attachement"),
        null=True, blank=False,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    is_valid = models.BooleanField(_("Is valid?"), default=False, blank=True,
                                   null=True)
    line_count = models.IntegerField(_("Number of lines"), default=0,
                                     blank=True, null=True)

    def filename(self):
        return os.path.basename(self.attachment.name)

    panels = [
        DocumentChooserPanel('attachment')
    ]
    base_form_class = PolicyDirectoryFileForm
