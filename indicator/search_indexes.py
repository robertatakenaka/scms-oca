# coding: utf-8
from haystack import indexes

from indicator import models


class IndicatorIndex(indexes.SearchIndex, indexes.Indexable):
    """
    Fields:
        text
    """
    created = indexes.CharField(model_attr="created", null=False)

    text = indexes.CharField(document=True, use_template=True)
    record_type = indexes.CharField(null=False)

    title = indexes.CharField(model_attr="title", null=True)
    description = indexes.CharField(model_attr="description", null=True)
    start_date = indexes.CharField(model_attr="start_date_year", null=True)
    end_date = indexes.CharField(model_attr="end_date_year", null=True)
    link = indexes.CharField(model_attr="link", null=True)
    record_status = indexes.CharField(model_attr="record_status", null=True)
    source = indexes.CharField(model_attr="source", null=True)
    total = indexes.CharField(model_attr="total", null=True)

    raw_data = indexes.CharField(null=True)

    # ForeignKeys
    classification = indexes.CharField(null=True)
    action = indexes.CharField(null=True)
    practice = indexes.CharField(null=True)
    communication_object = indexes.CharField(null=True)
    open_access_status = indexes.CharField(null=True)
    use_license = indexes.CharField(null=True)
    apc = indexes.CharField(null=True)

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

    def prepare_action(self, obj):
        return obj.action_and_practice and obj.action_and_practice.action.name

    def prepare_classification(self, obj):
        return obj.action_and_practice and obj.action_and_practice.classification

    def prepare_practice(self, obj):
        return obj.action_and_practice and obj.action_and_practice.practice.name

    def prepare_communication_object(self, obj):
        return (
            obj.scientific_production and
            obj.scientific_production.communication_object)

    def prepare_apc(self, obj):
        return (
            obj.scientific_production and
            obj.scientific_production.apc)

    def prepare_use_license(self, obj):
        return (
            obj.scientific_production and
            obj.scientific_production.use_license)

    def prepare_open_access_status(self, obj):
        return (
            obj.scientific_production and
            obj.scientific_production.open_access_status)

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
