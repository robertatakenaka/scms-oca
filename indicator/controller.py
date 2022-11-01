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
from scholarly_articles import controller as scholarly_articles_controller
from location.models import Location
from institution.models import Institution
from usefulmodels.models import Practice, State, Action, Country

from .models import Indicator, ActionAndPractice, ScientificProduction
from . import choices

User = get_user_model()


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
    #_add_param_for_action_and_practice(params, action_and_practice)
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


def build_code(indicator):
    # https://drive.google.com/drive/folders/1_J8iKhr_gayuBqtvnSWreC-eBnxzY9rh
    # IDENTIDADE sugerido:
    #      (seq + action + classification) +
    #      (created + creator_id) +
    #      (validity + previous + posterior) +
    #      (title)
    # ID melhorado:
    #    action + classification + practice + scope + seq

    return "--".join([
        indicator.action_and_practice.action.code or indicator.action_and_practice.action.name,
        indicator.action_and_practice.classification,
        indicator.action_and_practice.practice.code or indicator.action_and_practice.practice.name,
        indicator.scope,
        indicator.measurement,
        str(indicator.seq),
        indicator.created.isoformat()[:10]
    ]).lower()


##############################################################################
def number_of_actions(
        creator_id,
        ):
    title = "Número de ações em Ciência Aberta"
    scope = choices.CHRONOLOGICAL
    measurement = choices.FREQUENCY

    items = []
    items.extend(_number_of_actions(EducationDirectory))
    items.extend(_number_of_actions(EventDirectory))
    items.extend(_number_of_actions(InfrastructureDirectory))
    items.extend(_number_of_actions(PolicyDirectory))
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
    indicator.computed = {
        "items": list(_get_ranking_items(
            items, ['action__name', 'classification']))
    }
    indicator.description = "geral"
    indicator.total = len(items)
    indicator.creator_id = creator_id
    indicator.save()


def number_of_actions_with_practice(
        creator_id,
        ):
    title = "Número de práticas em Ciência Aberta"
    scope = choices.CHRONOLOGICAL
    measurement = choices.FREQUENCY

    items = []
    items.extend(_number_of_actions(EducationDirectory))
    items.extend(_number_of_actions(EventDirectory))
    items.extend(_number_of_actions(InfrastructureDirectory))
    items.extend(_number_of_actions(PolicyDirectory))
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
    indicator.computed = {
        'items': list(items),
        'cat1_name': 'practice__name',
        'cat2_name': 'action__name',
    }
    indicator.description = "geral"
    indicator.total = len(items)
    indicator.creator_id = creator_id
    indicator.save()


def _number_of_actions(
        model,
        action__name=None,
        ):
    args = [
        'action__name',
        'classification',
        'practice__name',
    ]
    if action__name:
        args.append(action__name)
    return model.objects.values(
            *args
        ).annotate(
            count=Count('id')
        ).order_by('count').iterator()


def number_of_actions_by_location(
        creator_id,
        ):
    title = "Número de ações em Ciência Aberta por "
    scope = choices.CHRONOLOGICAL
    measurement = choices.FREQUENCY

    items = []
    items.extend(_number_of_actions(EducationDirectory))
    items.extend(_number_of_actions(EventDirectory))
    items.extend(_number_of_actions(InfrastructureDirectory))
    items.extend(_number_of_actions(PolicyDirectory))
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
    indicator.computed = {
        'items': list(items),
        'cat1_name': 'practice__name',
        'cat2_name': 'action__name',
    }
    indicator.description = "geral"
    indicator.total = len(items)
    indicator.creator_id = creator_id
    indicator.save()


def _number_of_actions(
        model,
        action__name=None,
        ):
    args = [
        'action__name',
        'classification',
        'practice__name',
    ]
    if action__name:
        args.append(action__name)
    return model.objects.values(
            *args
        ).annotate(
            count=Count('id')
        ).order_by('count').iterator()


##############################################################################
def number_of_action_classification_and_practice_by_institution(
        title,
        action,
        creator_id,
        ):
    """
    Generate indicator according to the provided parameters

    Parameters
    ----------
    title : str
    action : Action

    Returns
    -------
    Indicator

    """
    scope = choices.INSTITUTIONAL
    standard_attribute = 'institutions'
    alternative_attribute = 'organization'
    measurement = choices.FREQUENCY

    indicators_data = {}
    for result in get_numbers_of_action_classification_and_practice(
            action, EducationDirectory,
            get_institutions_ranking,
            standard_attribute):
        register_indicator_of_action_classification_and_practice(
            action=action,
            scope=scope,
            title=title,
            data=result,
            measurement=measurement,
            creator_id=creator_id,
            observation='institution',
            education_results=result['raw_data'],
        )

    for result in get_numbers_of_action_classification_and_practice(
            action, EventDirectory,
            get_institutions_ranking,
            standard_attribute, alternative_attribute):
        register_indicator_of_action_classification_and_practice(
            action=action,
            scope=scope,
            title=title,
            data=result,
            measurement=measurement,
            creator_id=creator_id,
            observation='organization',
            event_results=result['raw_data'],
        )

    for result in get_numbers_of_action_classification_and_practice(
            action, InfrastructureDirectory,
            get_institutions_ranking,
            standard_attribute):
        register_indicator_of_action_classification_and_practice(
            action=action,
            scope=scope,
            title=title,
            data=result,
            measurement=measurement,
            creator_id=creator_id,
            observation='institution',
            infrastructure_results=result['raw_data'],
        )

    for result in get_numbers_of_action_classification_and_practice(
            action, PolicyDirectory,
            get_institutions_ranking,
            standard_attribute):
        register_indicator_of_action_classification_and_practice(
            action=action,
            scope=scope,
            title=title,
            data=result,
            measurement=measurement,
            creator_id=creator_id,
            observation='institution',
            policy_results=result['raw_data'],
        )


def _number_of_actions_by_institutions(
        creator_id,
        model,
        action,
        institution_name,
        ):

    dataset = model.objects.filter(action=action)

    summarized = dataset.values(
        'classification',
        'practice__name',
        institution_name,
    ).annotate(
        count=Count('id')
    ).order_by('count').iterator()

    scope = choices.INSTITUTIONAL
    measurement = choices.FREQUENCY
    observation = 'action'

    title = "Número de {} por institutição".format(action.name)

    indicator = create_record(
        title=title,
        action=action,
        classification=None,
        practice=None,
        scope=scope,
        measurement=measurement,
        creator_id=creator_id,
        # thematic_areas=thematic_areas,
        # institutions=institutions,
        # locations=locations,
        start_date_year=years[0] if years else None,
        end_date_year=years[-1] if years else None,
    )

    indicator.computed = {
        "items": list(_get_ranking_items(
            summarized, [institution_name]))
    }
    indicator.total = len(indicator.computed['items'])

    indicator.creator_id = creator_id
    indicator.save()


###########################################################################


def number_of_action_classification_and_practice_by_state(
        title,
        action,
        creator_id,
        ):
    """
    Generate indicator according to the provided parameters

    Parameters
    ----------
    title : str
    action : Action

    Returns
    -------
    Indicator

    """
    scope = choices.GEOGRAPHIC
    measurement = choices.FREQUENCY

    for result in get_numbers_of_action_classification_and_practice(
            action, EducationDirectory,
            get_locations_ranking, 'locations'):
        register_indicator_of_action_classification_and_practice(
            action=action,
            scope=scope,
            title=title,
            data=result,
            measurement=measurement,
            creator_id=creator_id,
            observation='location',
            education_results=result['raw_data'],
        )

    for result in get_numbers_of_action_classification_and_practice(
            action, EventDirectory,
            get_locations_ranking, 'locations'):
        register_indicator_of_action_classification_and_practice(
            action=action,
            scope=scope,
            title=title,
            data=result,
            measurement=measurement,
            creator_id=creator_id,
            observation='location',
            event_results=result['raw_data'],
        )

    for result in get_numbers_of_action_classification_and_practice(
            action, InfrastructureDirectory,
            get_locations_ranking, 'locations'):
        register_indicator_of_action_classification_and_practice(
            action=action,
            scope=scope,
            title=title,
            data=result,
            measurement=measurement,
            creator_id=creator_id,
            observation='location',
            infrastructure_results=result['raw_data'],
        )

    for result in get_numbers_of_action_classification_and_practice(
            action, PolicyDirectory,
            get_locations_ranking, 'locations'):
        register_indicator_of_action_classification_and_practice(
            action=action,
            scope=scope,
            title=title,
            data=result,
            measurement=measurement,
            creator_id=creator_id,
            observation='location',
            policy_results=result['raw_data'],
        )


def _number_of_actions_by_locations(
        creator_id,
        model,
        action,
        location_name,
        ):

    dataset = model.objects.filter(action=action)

    summarized = dataset.values(
        'classification',
        'practice__name',
        location_name,
    ).annotate(
        count=Count('id')
    ).order_by('count').iterator()

    scope = choices.INSTITUTIONAL
    measurement = choices.FREQUENCY
    observation = 'action'

    title = "Número de {} por institutição".format(action.name)

    indicator = create_record(
        title=title,
        action=action,
        classification=None,
        practice=None,
        scope=scope,
        measurement=measurement,
        creator_id=creator_id,
        # thematic_areas=thematic_areas,
        # institutions=institutions,
        # locations=locations,
        start_date_year=years[0] if years else None,
        end_date_year=years[-1] if years else None,
    )

    indicator.computed = {
        "items": list(_get_ranking_items(
            summarized, [location_name]))
    }
    indicator.total = len(indicator.computed['items'])

    indicator.creator_id = creator_id
    indicator.save()

##########################################################################

def get_numbers_of_action_classification_and_practice(
        action, model, ranking_calculation,
        standard_attribute, alternative_attribute=None):
    """
    Faz a consulta em um dado modelo (`model`) pela `action`
    """
    selected_attribute = alternative_attribute or standard_attribute

    for row in get_classification_and_practice(model, action):
        if not row['count']:
            continue

        key = (row['classification'], row['practice__name'])

        items = model.objects.filter(
            action=action,
            classification=row['classification'],
            practice__name=row['practice__name'],
        )

        result = {}
        result['classification'] = row['classification']
        result['practice'] = row['practice__name']
        result['raw_data'] = items.iterator()
        result['ranking'] = ranking_calculation(
            items, selected_attribute, standard_attribute
        )

        yield result


def get_classification_and_practice(model, action):
    """
    >>> City.objects.values('country__name') \
          .annotate(country_population=Sum('population')) \
          .order_by('-country_population')
    [
      {'country__name': u'China', 'country_population': 309898600},
      {'country__name': u'United States', 'country_population': 102537091},
      {'country__name': u'India', 'country_population': 100350602},
      {'country__name': u'Japan', 'country_population': 65372000},
      {'country__name': u'Brazil', 'country_population': 38676123},
      '...(remaining elements truncated)...'
    ]
    """
    return model.objects.filter(action=action).values(
        'classification',
        'practice__name',
    ).annotate(count=Count('id')).iterator()


#########################################################################

def get_institutions_ranking(items, selected_attribute, standard_attribute):
    """
    Parameters
    ----------
    items : QuerySet
    selected_attribute : str (ex.: 'organization')
    standard_attribute : str (ex.: 'institutions')

    """

    # https://docs.djangoproject.com/en/4.1/ref/models/querysets/#values
    #
    # >>> from django.db.models import Count
    # >>> Blog.objects.values('entry__authors', entries=Count('entry'))
    # <QuerySet [{'entry__authors': 1, 'entries': 20}, {'entry__authors': 1, 'entries': 13}]>
    # >>> Blog.objects.values('entry__authors').annotate(entries=Count('entry'))
    # <QuerySet [{'entry__authors': 1, 'entries': 33}]>

    selected_attribute = f"{selected_attribute}__name"
    for item in items.values(
                selected_attribute,
            ).annotate(
                count=Count(selected_attribute),
            ).order_by('-count').iterator():

        if item[selected_attribute]:
            item['name'] = item.pop(selected_attribute)
            if item['name']:
                yield item


def get_locations_ranking(items, ign1=None, ign2=None):
    """
    Parameters
    ----------
    items : QuerySet
    context_attribute : str (ex.: 'organization')
    standardized_name : str (ex.: 'institutions')

    """

    # https://docs.djangoproject.com/en/4.1/ref/models/querysets/#values
    #
    # >>> from django.db.models import Count
    # >>> Blog.objects.values('entry__authors', entries=Count('entry'))
    # <QuerySet [{'entry__authors': 1, 'entries': 20}, {'entry__authors': 1, 'entries': 13}]>
    # >>> Blog.objects.values('entry__authors').annotate(entries=Count('entry'))
    # <QuerySet [{'entry__authors': 1, 'entries': 33}]>

    try:
        for item in items.values(
                    'locations__state__acronym',
                ).annotate(
                    count=Count('locations__state__acronym')
                ).order_by('-count').iterator():
            try:
                item['name'] = item.pop('locations__state__acronym')
                if item['name']:
                    yield item
            except:
                pass
    except:
        pass
    try:
        for item in items.values(
                    'institutions__location__state__acronym',
                ).annotate(
                    count=Count('institutions__location__state__acronym')
                ).order_by('-count').iterator():
            try:
                item['name'] = item.pop('institutions__location__state__acronym')
                if item['name']:
                    yield item
            except:
                pass
    except:
        pass


#########################################################################


def register_indicator_of_action_classification_and_practice(
        action,
        scope,
        title,
        data,
        measurement,
        creator_id,
        observation,
        education_results=None,
        event_results=None,
        infrastructure_results=None,
        policy_results=None,
        thematic_areas=None,
        institutions=None,
        locations=None,
        start_date_year=None,
        end_date_year=None,
        ):

    # cria uma instância de Indicator
    title = title.replace(
        "[LABEL]",
        f"{action} {data['classification']} {data['practice']}",
    )

    logging.info(title)
    logging.info(data)

    indicator = create_record(
        title=title,
        action=action,
        classification=data['classification'],
        practice=Practice.objects.get(name=data['practice']),
        scope=scope,
        measurement=measurement,
        creator_id=creator_id,
        thematic_areas=thematic_areas,
        institutions=institutions,
        locations=locations,
        start_date_year=start_date_year,
        end_date_year=end_date_year,
    )

    computed = generate_computed(action.name, observation, measurement, data)
    indicator.computed = computed

    indicator.total = len(computed['items'])

    # if education_results:
    #     indicator.education_results.set(education_results)
    # if event_results:
    #     indicator.event_results.set(event_results)
    # if infrastructure_results:
    #     indicator.infrastructure_results.set(infrastructure_results)
    # if policy_results:
    #     indicator.policy_results.set(policy_results)

    # indicator.raw_data = save_raw_data(indicator)
    # TODO atualizar link e source
    # indicator.link = ''
    # indicator.source = ''

    indicator.creator_id = creator_id
    indicator.save()
    # retorna a instância de Indicator
    return indicator


def save_raw_data(indicator):
    csv_buffer = StringIO()
    fieldnames = ['action', 'qualification', 'practice', 'observation', 'measurement', 'name', 'count', ]
    writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)

    writer.writeheader()

    # csv_file = ContentFile(csv_buffer.getvalue().encode('utf-8'))
    # doc.csvfile.save('output.csv', csv_file)

    # create csv


def generate_computed(action, observation, measurement, data):
    """
    {"items": [
        {"name": "Universidade de São Paulo - Localização: Country: Brasil | Estado: São Paulo | Cidade: Botucatu",
        "count": 6, "institutions": 1845},
        {"name": "  - Localização: Country: Brasil | Estado: virtual | Cidade: virtual",
        "count": 3, "institutions": 1847}, 
        {"name": "Universidade Federal do Estado de São Paulo - Localização: Country: Brasil | Estado: São Paulo | Cidade: Guarulhos", "count": 2, "institutions": 1848}, {"name": "Universidade Federal de São Carlos - Localização: Country: Brasil | Estado: São Paulo | Cidade: None", "count": 1, "institutions": 1773}, {"name": "Scientific Electronic Library Online - Localização: Country: Brasil | Estado: São Paulo | Cidade: São Paulo", "count": 1, "institutions": 1839}, {"name": "Instituto Brasileiro de Informação em Ciência e Tecnologia - Localização: Country: Brasil | Estado: Distrito Federal | Cidade: Brasília", "count": 1, "institutions": 1840}], 
    "action": "infraestrutura", 
    "practice": "literatura em acesso aberto", 
    "measurement": "FREQUENCY", 
    "observation": "institution", 
    "classification": "repositório"}
    """
    json = {}
    json['header'] = [
        {"action": action},
        {"qualification": data['classification']},
        {"practice": data['practice']},
        {"observation": observation},
        {"measurement": measurement},
    ]
    json['items'] = list(data['ranking'])
    return json


def complete_affiliations_country():
    for aff in Affiliations.objects.filter(
            country__isnull=True, official__isnull=False).iterator():
        aff.country.acronym = "BR"
        aff.save()


##########################################################################

def number_of_journals(
        creator_id,
        oa_status_flag=False,
        use_license_flag=False,
        publisher_institution_type_flag=False,
        thematic_areas_flag=False,
        publisher_UF_flag=False,
        ppgs_flag=False,
        ):
    summarized = scholarly_articles_controller.number_journals(
        oa_status_flag,
        use_license_flag,
        publisher_institution_type_flag,
        thematic_areas_flag,
        publisher_UF_flag,
        ppgs_flag,
    )
    # identifica action, classification, practice
    action = Action.objects.get(name__icontains='produção')
    practice = Practice.objects.get(name='literatura em acesso aberto')
    classification = "literatura científica"

    action_and_practice = ActionAndPractice.get_or_create(
        action, classification, practice)
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

    if thematic_areas_flag and ppgs_flag:
        # TODO
        raise NotImplementedError(
            "Number of journals by thematic_areas and ppgs")
    elif thematic_areas_flag and publisher_institution_type_flag:
        # TODO
        raise NotImplementedError(
            "Number of journals by thematic_areas and publishers")
    elif oa_status_flag:
        _title = "tipo de Acesso Aberto"
        scope = "GERAL"
        measurements = [choices.FREQUENCY]
        name_keys = ['open_access_status']

    elif use_license_flag:
        _title = "licença de uso"
        scope = "GERAL"
        measurements = [choices.FREQUENCY]
        name_keys = ['use_license']

    elif publisher_institution_type_flag:
        _title = "tipo de instituição publicadora"
        scope = choices.INSTITUTIONAL
        measurements = [choices.FREQUENCY]
        name_keys = ['publisher__institution_type']

    elif thematic_areas_flag:
        _title = "áreas temáticas"
        scope = choices.THEMATIC
        measurements = [choices.FREQUENCY]
        name_keys = [
            'thematic_areas__level0',
            'thematic_areas__level1',
            'thematic_areas__level2',
        ]

    elif publisher_UF_flag:
        _title = "UF"
        scope = choices.GEOGRAPHIC
        measurements = [choices.FREQUENCY]
        name_keys = ['publisher__location__state__acronym']

    elif ppgs_flag:
        _title = "PPGs"
        scope = choices.INSTITUTIONAL
        measurements = [choices.FREQUENCY]
        name_keys = [
            'contributors__affiliation__official__name',
            'contributors__affiliation__official__level_1',
            'contributors__affiliation__official__level_2',
            'contributors__affiliation__official__level_3',
            'contributors__affiliation__official__location__city__name',
            'contributors__affiliation__official__location__state__acronym',
        ]

    title = "Número de periódicos em acesso aberto por {}".format(
        _title,
    )
    for measurement in measurements:
        indicator = create_record(
            title=title,
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
            start_date_year=datetime.now().year,
        )
        indicator.computed = {
            "items": list(_get_ranking_items(summarized, name_keys))
        }
        indicator.total = len(indicator.computed['items'])
        indicator.creator_id = creator_id
        indicator.save()


def scientific_production_institutions_ranking(
        creator_id,
        oa_status_items=None,
        years=None,
        BR_affiliations=False,
        ):

    # identifica action, classification, practice
    action = Action.objects.get(name__icontains='produção')
    practice = Practice.objects.get(name='literatura em acesso aberto')
    classification = "literatura científica"

    action_and_practice = ActionAndPractice.get_or_create(
        action, classification, practice)
    observation = 'journal-article'

    # seleciona produção científica brasileira e de acesso aberto
    scope = choices.INSTITUTIONAL
    measurement = choices.FREQUENCY

    years, years_as_str = _get_years_param_value(years)
    oa_status_items, oa_status = _get_oa_status_param_value(oa_status_items)

    scientific_production = ScientificProduction.get_or_create(
        communication_object='journal-article',
        open_access_status=oa_status,
        use_license=None,
        apc=None,
    )

    dataset = _get_dataset(oa_status_items, years_as_str, BR_affiliations)

    args = []
    if len(years) == 1:
        args.append('year')
        year = f" de {years[0]}"
    else:
        year = ""
    if BR_affiliations:
        name_keys = [
            'contributors__affiliation__official__name',
            'contributors__affiliation__official__location__state__acronym']
    else:
        name_keys = ['contributors__affiliation__name', ]
    args.extend(name_keys)
    logging.info(args)

    title = "Número de artigos{} em acesso aberto{} por instituição".format(
        year, oa_status and f" {oa_status}" or '',
    )

    indicator = create_record(
        title=title,
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
        start_date_year=years[0] if years else None,
        end_date_year=years[-1] if years else None,
    )

    summarized = dataset.values(
                *args
            ).annotate(
                count=Count('id'),
            ).order_by('count').iterator()

    indicator.computed = {
        "items": list(_get_ranking_items(summarized, name_keys))
    }
    indicator.total = len(indicator.computed['items'])
    indicator.description = "" if oa_status_items else 'geral'
    indicator.creator_id = creator_id
    indicator.save()


def _get_ranking_items(items, name_keys):
    for item in items:
        logging.info(item)
        if item['count']:
            name = " | ".join([
                item.get(k) or ''
                for k in name_keys
            ])
            item.update(
                {
                    "name": name or '',
                    "count": item['count'],
                }
            )
            yield item


def _get_dataset(oa_status_items, years_as_str, BR_affiliations=None):
        # query
    qs = dict(
        open_access_status__in=oa_status_items,
        year__in=years_as_str,
    )
    if BR_affiliations:
        # adiciona filtro para selecionar BR
        qs['contributors__affiliation__official__isnull'] = False
        qs['contributors__affiliation__country__acron2'] = 'BR'

    # obtém dataset
    logging.info(qs)
    return ScholarlyArticles.objects.filter(**qs)


def _get_oa_status_param_value(oa_status_items):
    oa_status_items = oa_status_items or (
        'gold', 'bronze', 'green', 'hybrid', )
    if len(oa_status_items) == 1:
        oa_status = oa_status_items[0]
    else:
        oa_status = ""
    return oa_status_items, oa_status


def get_years_range(year_numbers):
    return range(datetime.now().year - year_numbers, datetime.now().year + 1)


def _get_years_param_value(years, year_numbers=10):
    # default last 10 years
    years = years or list(get_years_range(year_numbers))
    years_as_str = [str(y) for y in years]
    return years, years_as_str


def generate_open_access_status_evolution(
        creator_id,
        years=None,
        BR_affiliations=False,
        oa_status_items=None,
        ):
    """

    """
    oa_status_items, oa_status = _get_oa_status_param_value(oa_status_items)
    years, years_as_str = _get_years_param_value(years)

    # identifica action, classification, practice
    action = Action.objects.get(name__icontains='produção')
    practice = Practice.objects.get(name='literatura em acesso aberto')
    classification = "literatura científica"
    action_and_practice = ActionAndPractice.get_or_create(
        action, classification, practice)

    # características do indicador
    scope = choices.CHRONOLOGICAL
    measurement = choices.EVOLUTION
    observation = 'journal-article'

    scientific_production = ScientificProduction.get_or_create(
        communication_object='journal-article',
        open_access_status=oa_status,
        use_license=None,
        apc=None,
    )

    # obtém dataset
    dataset = _get_dataset(oa_status_items, years_as_str, BR_affiliations)

    # argumentos para values()
    values_args = ['year', 'open_access_status', ]
    if oa_status:
        CATEGORY = 'use_license'
        values_args.append('use_license')
    else:
        CATEGORY = 'open_access_status'

    indicator = create_record(
        title='Evolução do número de artigos em acesso aberto{} {}-{}'.format(
            oa_status and f" {oa_status}" or '', years[0], years[-1]),
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
        start_date_year=years[0] if years else None,
        end_date_year=years[-1] if years else None,
    )
    indicator.start_date_year = years[0]
    indicator.end_date_year = years[-1]

    items = dataset.values(
                *values_args
            ).annotate(
                count=Count('id'),
            ).iterator()
    indicator.computed = {
        'items': list(items),
        'cat1_name': 'year',
        'cat2_name': CATEGORY,
        'cat1_values': years_as_str,
    }
    indicator.description = "" if oa_status_items else 'geral'
    indicator.creator_id = creator_id
    indicator.save()
