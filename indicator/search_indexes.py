# coding: utf-8
from haystack import indexes

from indicator import models


class IndicatorIndex(indexes.SearchIndex, indexes.Indexable):
    """
    Fields:
        text
    """
    text = indexes.CharField(document=True, use_template=True)
    record_type = indexes.CharField(null=False)

    title = indexes.CharField(model_attr="title", null=True)
    description = indexes.CharField(model_attr="description", null=True)
    classification = indexes.CharField(model_attr="classification", null=True)
    start_date = indexes.CharField(model_attr="start_date", null=True)
    end_date = indexes.CharField(model_attr="end_date", null=True)
    link = indexes.CharField(model_attr="link", null=True)
    record_status = indexes.CharField(model_attr="record_status", null=True)
    source = indexes.CharField(model_attr="source", null=True)

    raw_data = indexes.CharField(null=True)

    # ForeignKeys
    action = indexes.CharField(model_attr="action", null=True)
    practice = indexes.CharField(model_attr="practice", null=True)

    # ManyToMany
    keywords = indexes.MultiValueField(null=True)
    thematic_areas = indexes.MultiValueField(null=True)
    institutions = indexes.MultiValueField(null=True)
    locations = indexes.MultiValueField(null=True)

    # Location
    countries = indexes.MultiValueField(null=True)
    cities = indexes.MultiValueField(null=True)
    states = indexes.MultiValueField(null=True)
    regions = indexes.MultiValueField(null=True)

    def prepare_file_csv(self, obj):
        return obj.raw_data and obj.raw_data.url

    def prepare_record_type(self, obj):
        return "indicator"

    def prepare_directory_type(self, obj):
        return ""

    def prepare_institutions(self, obj):
        if obj.institutions:
            return [institution.name for institution in obj.institutions.all()]

    def prepare_thematic_areas(self, obj):
        thematic_areas = set()
        if obj.thematic_areas:
            for thematic_area in obj.thematic_areas.all():
                thematic_areas.add(thematic_area.level0)
                thematic_areas.add(thematic_area.level1)
                thematic_areas.add(thematic_area.level2)
            return thematic_areas

    def prepare_keywords(self, obj):
        if obj.keywords.names():
            return [name for name in obj.keywords.names()]

    def prepare_countries(self, obj):
        countries = set()
        if obj.locations.all():
            for loc in obj.locations.all():
                try:
                    countries.add(loc.country.name)
                except AttributeError:
                    continue
        if obj.institutions.all():
            for inst in obj.institutions.all():
                try:
                    countries.add(inst.location.country.name)
                except AttributeError:
                    continue
            return countries

    def prepare_cities(self, obj):
        cities = set()
        if obj.locations.all():
            for loc in obj.locations.all():
                try:
                    cities.add(loc.city.name)
                except AttributeError:
                    continue
        if obj.institutions.all():
            for inst in obj.institutions.all():
                try:
                    cities.add(inst.location.city.name)
                except AttributeError:
                    continue
            return cities

    def prepare_states(self, obj):
        states = set()
        if obj.locations.all():
            for loc in obj.locations.all():
                try:
                    states.add(loc.state.name)
                except AttributeError:
                    continue
        if obj.institutions.all():
            for inst in obj.institutions.all():
                try:
                    states.add(inst.location.state.name)
                except AttributeError:
                    continue
            return states

    def prepare_regions(self, obj):
        regions = set()
        if obj.locations.all():
            for loc in obj.locations.all():
                try:
                    regions.add(loc.state.region)
                except AttributeError:
                    continue
        if obj.institutions.all():
            for inst in obj.institutions.all():
                try:
                    regions.add(inst.location.states.region)
                except AttributeError:
                    continue
            return regions

    def get_model(self):
        return models.Indicator

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(record_status="PUBLISHED")
