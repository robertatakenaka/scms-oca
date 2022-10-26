from django.db import models
from django.utils.translation import gettext as _
from taggit.managers import TaggableManager
from wagtail.admin.edit_handlers import FieldPanel

from core.models import CommonControlField

from . import choices
from . forms import IndicatorDirectoryForm
from usefulmodels.models import Action, Practice, ThematicArea
from institution.models import Institution
from location.models import Location
from education_directory.models import EducationDirectory
from event_directory.models import EventDirectory
from infrastructure_directory.models import InfrastructureDirectory
from policy_directory.models import PolicyDirectory


class Indicator(CommonControlField):

    code = models.CharField(_("Code"), max_length=555, null=False, blank=False)

    title = models.CharField(_("Title"), max_length=255, null=False, blank=False)
    description = models.TextField(_("Description"), max_length=1000,
                                   null=True, blank=True)

    action = models.ForeignKey(Action, verbose_name=_("Action"), null=True, blank=True, on_delete=models.SET_NULL)
    classification = models.CharField(_("Classification"), choices=choices.classification,
                                      max_length=255, null=True, blank=True)
    practice = models.ForeignKey(Practice, verbose_name=_("Practice"),
                                 null=True, blank=True, on_delete=models.SET_NULL)
    scope = models.CharField(_('Scope'), choices=choices.SCOPE, max_length=20, null=True)
    measurement = models.CharField(_('Measurement'), choices=choices.MEASUREMENT_TYPE, max_length=25, null=True)

    thematic_areas = models.ManyToManyField(ThematicArea, verbose_name=_("Thematic Area"), blank=True)
    institutions = models.ManyToManyField(Institution, verbose_name=_("Institution"), blank=True)
    locations = models.ManyToManyField(Location, verbose_name=_("Location"),  blank=True)
    start_date = models.DateField(_("Start Date"), max_length=255, null=True, blank=True)
    end_date = models.DateField(_("End Date"), max_length=255, null=True, blank=True)

    link = models.URLField(_("Link"), null=True, blank=True)
    raw_data = models.FileField(_("CSV File"), null=True, blank=True)
    computed = models.JSONField(_("JSON File"), null=True, blank=True)
    total = models.IntegerField(_("Observations number"), null=True, default=None)

    # event_results = models.ManyToManyField(EventDirectory, blank=True)
    # education_results = models.ManyToManyField(EducationDirectory, blank=True)
    # infrastructure_results = models.ManyToManyField(InfrastructureDirectory, blank=True)
    # policy_results = models.ManyToManyField(PolicyDirectory, blank=True)

    keywords = TaggableManager(_("Keywords"), blank=True)

    record_status = models.CharField(_("Record status"), choices=choices.status,
                                     max_length=255, null=True, blank=True)
    source = models.CharField(_("Source"), max_length=255, null=True, blank=True)

    validity = models.CharField(_("Record validity"), choices=choices.VALIDITY,
                                     max_length=255, null=True, blank=True)
    previous_record = models.ForeignKey(
        'self',
        verbose_name=_("Previous Record"),
        related_name="predecessor_register",
        on_delete=models.SET_NULL,
        max_length=255, null=True, blank=True)
    posterior_record = models.ForeignKey(
        'self',
        verbose_name=_("Posterior Record"),
        related_name="successor_register",
        on_delete=models.SET_NULL,
        max_length=255, null=True, blank=True)
    seq = models.IntegerField(_('Sequential number'), null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['start_date']),
            models.Index(fields=['end_date']),
            models.Index(fields=['practice']),
            models.Index(fields=['action']),
            models.Index(fields=['classification']),
            models.Index(fields=['source']),
            models.Index(fields=['record_status']),
        ]

    panels = [
        FieldPanel('code'),
        FieldPanel('title'),
        FieldPanel('action'),
        FieldPanel('classification'),
        FieldPanel('practice'),
        FieldPanel('measurement'),
        FieldPanel('scope'),
        FieldPanel('seq'),

        FieldPanel('total'),
        FieldPanel('computed'),
        FieldPanel('raw_data'),
        FieldPanel('link'),

        FieldPanel('start_date'),
        FieldPanel('end_date'),
        # FieldPanel('institutions'),
        # FieldPanel('locations'),
        # FieldPanel('thematic_areas'),
        FieldPanel('description'),
        FieldPanel('keywords'),

        FieldPanel('posterior_record'),
        FieldPanel('previous_record'),
        FieldPanel('record_status'),
        FieldPanel('source'),
        FieldPanel('validity'),
    ]

    # https://drive.google.com/drive/folders/1_J8iKhr_gayuBqtvnSWreC-eBnxzY9rh
    # IDENTIDADE sugerido:
    #      (seq + action + classification) +
    #      (created + creator_id) +
    #      (validity + previous + posterior) +
    #      (title)
    # ID melhorado:
    #    action + classification + practice + scope + seq
    def __unicode__(self):
        return f"{self.action} {self.classification} {self.practice} {self.scope} {self.seq} "

    def __str__(self):
        return f"{self.action} {self.classification} {self.practice} {self.scope} {self.seq} "

    base_form_class = IndicatorDirectoryForm
