from datetime import datetime
import logging
import csv
import io
import json

from django.db.models import Count, Sum
from django.utils.translation import gettext as _
from django.core.files.base import ContentFile
from django.db.models import Q
from django.contrib.auth import get_user_model

from education_directory.models import EducationDirectory
from event_directory.models import EventDirectory
from infrastructure_directory.models import InfrastructureDirectory
from policy_directory.models import PolicyDirectory

from education_directory.choices import classification as education_choices
from event_directory.choices import classification as event_choices
from infrastructure_directory.choices import classification as infra_choices
from policy_directory.choices import classification as policy_choices
from scholarly_articles.models import ScholarlyArticles, Affiliations
from location.models import Location
from institution.models import Institution
from usefulmodels.models import Practice, State, Action, Country

from .models import Indicator, ActionAndPractice, ScientificProduction
from . import choices

User = get_user_model()


OA_STATUS_ITEMS = ('gold', 'bronze', 'green', 'hybrid', )


def _get_ranking_items(items, name_keys):
    for item in items:
        logging.info(item)
        if item['count']:
            name = "|".join([
                item[k] or ''
                for k in name_keys
                if item.get(k)
            ])
            if not name:
                logging.info("$$$$$$$$$$$$$$$$$")
                logging.error(item)
                logging.error(name_keys)
                continue
            item.update(
                {
                    "name": name or '',
                    "count": item['count'],
                }
            )
            yield item


def affiliations_numbers():
    stats = {}
    stats['institution__total'] = Institution.objects.count()
    inst__country = Institution.objects.filter(
        location__country__isnull=False)
    inst__state = Institution.objects.filter(
        location__state__isnull=False)
    inst__city = Institution.objects.filter(
        location__city__isnull=False)
    inst__country__BR = Institution.objects.filter(
        location__country__acron2='BR')
    stats['institution__city'] = inst__city.count()
    stats['institution__state'] = inst__state.count()
    stats['institution__country'] = inst__country.count()
    stats['institution__country__BR'] = inst__country__BR.count()

    stats['aff__total'] = Affiliations.objects.count()
    official = Affiliations.objects.filter(
        official__isnull=False,
    )
    official__country = official.filter(
        official__location__country__isnull=False)
    official__state = official.filter(
        official__location__state__isnull=False)
    official__city = official.filter(
        official__location__city__isnull=False)
    official__country__BR = official.filter(
        official__location__country__acron2='BR')

    stats['aff__official'] = official.count()
    stats['aff__official__city'] = official__city.count()
    stats['aff__official__state'] = official__state.count()
    stats['aff__official__country'] = official__country.count()
    stats['aff__official__country__BR'] = official__country__BR.count()
    stats['aff__country'] = Affiliations.objects.filter(
        country__isnull=False,
    ).count()
    stats['aff__country__BR'] = Affiliations.objects.filter(
        country__acron2='BR',
    ).count()
    return {
        "items": [
            {"name": k, "count": v}
            for k, v in stats.items()
        ]
    }


def qa():
    classifications = []
    classifications.extend([c[0] for c in education_choices])
    classifications.extend([c[0] for c in event_choices])
    classifications.extend([c[0] for c in infra_choices])
    classifications.extend([c[0] for c in policy_choices])

    for model in (EducationDirectory, InfrastructureDirectory, EventDirectory, PolicyDirectory):
        for item in model.objects.iterator():
            item.record_status = 'PUBLISHED'
            alt = []
            for classification in classifications:
                if classification in item.description.lower() or classification in item.title.lower():
                    alt.append(classification)
            if alt and item.classification not in alt:
                item.record_status = 'TO MODERATE'
            item.save()


def delete():
    for item in Indicator.objects.iterator():
        try:
            item.action_and_practice = None
            if item.thematic_areas:
                item.thematic_areas.clear()
            if item.institutions:
                item.institutions.clear()
            if item.locations:
                item.locations.clear()
            item.delete()
        except Exception as e:
            print(e)


def _add_param(params, name, value):
    if value:
        params[name] = value
    else:
        params[f'{name}__isnull'] = True


def _add_param_for_action_and_practice(params, action_and_practice):
    if action_and_practice:
        _add_param(params, "action_and_practice__action", action_and_practice.action)
        _add_param(params, "action_and_practice__classification", action_and_practice.classification)
        _add_param(params, "action_and_practice__practice", action_and_practice.practice)
    else:
        _add_param(params, "action_and_practice", None)


def _add_param_for_thematic_areas(params, thematic_areas):
    if thematic_areas:
        _add_param(params, "thematic_areas__level0", thematic_areas.level0)
        _add_param(params, "thematic_areas__level1", thematic_areas.level1)
        _add_param(params, "thematic_areas__level2", thematic_areas.level2)
    else:
        _add_param(params, "thematic_areas", None)


def _add_param_for_institutions(params, institutions):
    if institutions:
        _add_param(params, "institutions__name", institutions.name)
    else:
        _add_param(params, "institutions", None)


def _add_param_for_locations(params, locations):
    if locations:
        _add_param(params, "locations__city__name", locations.city__name)
        _add_param(params, "locations__state__acronym", locations.state__acronym)
        _add_param(params, "locations__country__acron2", locations.country__acron2)
    else:
        _add_param(params, "locations", None)


def create_record(
        title,
        action,
        classification,
        practice,
        scope,
        measurement,
        creator_id,
        scientific_production=None,
        thematic_areas=None,
        institutions=None,
        locations=None,
        start_date_year=None,
        end_date_year=None,
        ):
    """
    Cria uma nova instância de Indicator,
    adicionando / atualizando os atributos `seq` e outros relacionados com
    a versão do indicador

    Parameters
    ----------
    action : Action
    classification : str
    practice : Practice
    scope : choices.SCOPE
    measurement : choices.MEASUREMENT_TYPE
    """
    params = dict(
        scope=scope,
        measurement=measurement,
        posterior_record__isnull=True
    )
    _add_param(params, 'scientific_production', scientific_production)
    _add_param(params, 'start_date_year', start_date_year)
    _add_param(params, 'end_date_year', end_date_year)

    if any([action, classification, practice]):
        action_and_practice = ActionAndPractice.get_or_create(
            action, classification, practice
        )
    else:
        action_and_practice = None

    _add_param_for_thematic_areas(params, thematic_areas)
    _add_param_for_institutions(params, institutions)
    _add_param_for_locations(params, locations)
    try:
        logging.info(params)
        previous = Indicator.objects.filter(**params)[0]
        seq = (previous.seq or 0) + 1
        previous.validity = choices.OUTDATED
    except Exception as e:
        logging.exception(e)
        seq = 1
        previous = None

    logging.info("Create Indicator")
    logging.info(params)
    indicator = Indicator()
    indicator.seq = seq
    indicator.previous_record = previous
    indicator.posterior_record = None
    indicator.title = title
    indicator.validity = choices.CURRENT
    indicator.action_and_practice = action_and_practice
    indicator.scope = scope
    indicator.measurement = measurement
    indicator.scientific_production = scientific_production
    indicator.start_date_year = start_date_year
    indicator.end_date_year = end_date_year
    if institutions:
        indicator.institutions.set(institutions)
    if locations:
        indicator.locations.set(locations)
    if thematic_areas:
        indicator.thematic_areas.set(thematic_areas)
    if institutions:
        indicator.institutions.set(institutions)
    indicator.record_status = choices.PUBLISHED
    indicator.creator_id = creator_id
    indicator.save()

    if previous:
        previous.posterior_record = indicator
        previous.save()

    #indicator.code = build_code(indicator)
    indicator.save()
    return indicator


##############################################################################
def actions_numbers(
        creator_id,
        category_title,
        category_name,
        category_attributes,
        category2_name=None,
        category2_attributes=None
        ):
    title = "Número de ações em Ciência Aberta{}".format(category_title)
    scope = choices.GENERAL
    measurement = choices.FREQUENCY
    # category_attributes = ['action__name', 'classification']

    cats_attributes = category_attributes + (category2_attributes or [])
    items = []
    items.extend(_actions_numbers(EducationDirectory, cats_attributes))
    items.extend(_actions_numbers(EventDirectory, cats_attributes))
    items.extend(_actions_numbers(InfrastructureDirectory, cats_attributes))
    items.extend(_actions_numbers(PolicyDirectory, cats_attributes))
    indicator = create_record(
        title=title,
        action=None,
        classification=None,
        practice=None,
        scope=scope,
        measurement=measurement,
        creator_id=creator_id,
        # thematic_areas=thematic_areas,
        # institutions=institutions,
        # locations=locations,
        # start_date_year=start_date_year,
    )
    if category2_name:
        # cat1 = variável cujo valor é comum nos registros, por ex, year
        # cat1_name = practice__name
        # cat2_name = acton__name
        indicator.computed = {
            'items': list(items),
            'cat1_name': category_name,
            'cat2_name': category2_name,
        }
    else:
        indicator.computed = {
            "items": list(_get_ranking_items(items, category_attributes))
        }
    indicator.total = len(items)
    indicator.creator_id = creator_id
    indicator.save()


def _actions_numbers(
        model,
        category_attributes,
        ):
    return model.objects.values(
            *category_attributes
        ).annotate(
            count=Count('id')
        ).order_by('count').iterator()


##########################################################################

def journals_numbers(
        creator_id,
        category_title,
        category_attributes,
        ):
    summarized = _journals_numbers(category_attributes)

    action, classification, practice = (
        _get_scientific_production__action_classification_practice())

    observation = 'journal'

    # seleciona produção científica brasileira e de acesso aberto
    # scope = choices.INSTITUTIONAL
    # measurement = choices.FREQUENCY

    scientific_production = ScientificProduction.get_or_create(
        communication_object='journal',
        open_access_status=None,
        use_license=None,
        apc=None,
    )

    title = "Número de periódicos em acesso aberto por {}".format(
        category_title,
    )
    indicator = create_record(
        title=title,
        action=action,
        classification=classification,
        practice=practice,
        scope=choices.GENERAL,
        measurement=choices.FREQUENCY,
        creator_id=creator_id,
        scientific_production=scientific_production,
        # thematic_areas=thematic_areas,
        # institutions=institutions,
        # locations=locations,
        start_date_year=datetime.now().year,
    )
    indicator.computed = {
        "items": list(_get_ranking_items(summarized, category_attributes))
    }
    indicator.total = len(indicator.computed['items'])
    indicator.creator_id = creator_id
    indicator.save()


def _journals_numbers(
        category_attributes,
        ):
    articles_cat = (['open_access_status'], ['use_license'], )

    if category_attributes not in articles_cat:
        raise NotImplementedError(
            "Não implementado para %s" % category_attributes)

    filtered = ScholarlyArticles.objects.filter(
        open_access_status__in=['gold', 'bronze', 'green', 'hybrid']
    )
    summarized = filtered.values(
            *category_attributes
        ).annotate(
            count=Count("journal", distinct=True)
        )
    return summarized.order_by('count').iterator()


##########################################################################

def _get_scientific_production__action_classification_practice():
    # identifica action, classification, practice
    action = Action.objects.get(name__icontains='produção')
    practice = Practice.objects.get(name='literatura em acesso aberto')
    classification = "literatura científica"
    return action, classification, practice


def get_years_range(years_number=5):
    return list(range(
            datetime.now().year - years_number,
            datetime.now().year + 1))


def str_years_list(years_range):
    return [str(y) for y in years_range]

##########################################################################

def _concat_values(category_names, category_values):
    return " | ".join([
                category_values[k]
                for k in category_names
                if category_values.get(k)
            ])


def evolution_of_scientific_production_for_larger_groups(
        creator_id,
        category_title,
        category_name,
        category_attributes,
        years_range,
        ):
    """
    """
    if category_name in category_attributes:
        category_name = "_".join(category_attributes)
    # identifica action, classification, practice
    action, classification, practice = (
        _get_scientific_production__action_classification_practice())

    # características do indicador
    scope = choices.CHRONOLOGICAL
    measurement = choices.EVOLUTION
    observation = 'journal-article'

    scientific_production = ScientificProduction.get_or_create(
        communication_object='journal-article',
        open_access_status=None,
        use_license=None,
        apc=None,
    )
    years_range = years_range or get_years_range()
    years_as_str = str_years_list(years_range)

    # obtém dataset
    dataset = ScholarlyArticles.objects.filter(
        Q(contributors__affiliation__official__location__country__acron2='BR') |
        Q(contributors__affiliation__country__acron2='BR'),
        open_access_status__in=OA_STATUS_ITEMS,
        year__in=years_as_str,
    )
    for group in dataset.values(*category_attributes).iterator():
        indicator = create_record(
            title='Evolução do número de artigos {} em acesso aberto por {} {}-{}'.format(
                " de " + _concat_values(category_attributes, group),
                category_title,
                years_range[0],
                years_range[-1]),
            action=action,
            classification=classification,
            practice=practice,
            scope=scope,
            measurement=measurement,
            creator_id=creator_id,
            scientific_production=scientific_production,
            # thematic_areas=thematic_areas,
            # institutions=institutions,
            # locations=locations,
            start_date_year=years_range[0] if years_range else None,
            end_date_year=years_range[-1] if years_range else None,
        )
        summarized = dataset.filter(**group).values(
                    'year',
                    *category_attributes,
                ).annotate(
                    count=Count('id'),
                ).iterator()
        items = []
        for item in summarized:
            item.update({
                category_name: _concat_values(category_attributes, item)})
            items.append(item)
        indicator.computed = {
            'items': list(items),
            'cat1_name': 'year',
            'cat2_name': category_name,
            'cat1_values': years_as_str,
        }
        indicator.creator_id = creator_id
        indicator.save()


def evolution_of_scientific_production(
        creator_id,
        category_title,
        category_name,
        category_attributes,
        years_range,
        ):
    """
    """
    if category_name in category_attributes:
        category_name = "_".join(category_attributes)
    # identifica action, classification, practice
    action, classification, practice = (
        _get_scientific_production__action_classification_practice())

    # características do indicador
    scope = choices.CHRONOLOGICAL
    measurement = choices.EVOLUTION
    observation = 'journal-article'

    scientific_production = ScientificProduction.get_or_create(
        communication_object='journal-article',
        open_access_status=None,
        use_license=None,
        apc=None,
    )
    years_range = years_range or get_years_range()
    years_as_str = str_years_list(years_range)

    # obtém dataset
    dataset = ScholarlyArticles.objects.filter(
        Q(contributors__affiliation__official__location__country__acron2='BR') |
        Q(contributors__affiliation__country__acron2='BR'),
        open_access_status__in=OA_STATUS_ITEMS,
        year__in=years_as_str,
    )

    indicator = create_record(
        title='Evolução do número de artigos em acesso aberto por {} {}-{}'.format(
            category_title, years_range[0], years_range[-1]),
        action=action,
        classification=classification,
        practice=practice,
        scope=scope,
        measurement=measurement,
        creator_id=creator_id,
        scientific_production=scientific_production,
        # thematic_areas=thematic_areas,
        # institutions=institutions,
        # locations=locations,
        start_date_year=years_range[0] if years_range else None,
        end_date_year=years_range[-1] if years_range else None,
    )
    summarized = dataset.values(
                'year',
                *category_attributes,
            ).annotate(
                count=Count('id'),
            ).iterator()
    items = []
    for item in summarized:
        item.update({
            category_name: "|".join([
                item[k]
                for k in category_attributes
                if item.get(k)
            ])})
        items.append(item)
    indicator.computed = {
        'items': list(items),
        'cat1_name': 'year',
        'cat2_name': category_name,
        'cat1_values': years_as_str,
    }
    indicator.creator_id = creator_id
    indicator.save()
