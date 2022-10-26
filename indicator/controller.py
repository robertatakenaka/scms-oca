import csv
import io
import json

from django.db.models import Count
from django.utils.translation import gettext as _
from django.core.files.base import ContentFile

from education_directory.models import EducationDirectory
from event_directory.models import EventDirectory
from infrastructure_directory.models import InfrastructureDirectory
from policy_directory.models import PolicyDirectory

from education_directory.choices import classification as education_choices
from event_directory.choices import classification as event_choices
from infrastructure_directory.choices import classification as infra_choices
from policy_directory.choices import classification as policy_choices

from location.models import Location
from institution.models import Institution
from usefulmodels.models import Practice, State

from .models import Indicator
from . import choices


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


def create_record(
        title,
        action,
        classification,
        practice,
        scope,
        measurement,
        creator_id,
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
    try:
        previous = Indicator.objects.filter(
            action=action,
            practice=practice,
            classification=classification,
            scope=scope,
            measurement=measurement,
            posterior_record__isnull=True)[0]
        seq = (previous.seq or 0) + 1
        previous.validity = choices.OUTDATED
    except IndexError:
        seq = 1
        previous = None

    indicator = Indicator()
    indicator.seq = seq
    indicator.previous_record = previous
    indicator.posterior_record = None
    indicator.title = title
    indicator.validity = choices.CURRENT
    indicator.action = action
    indicator.practice = practice
    indicator.classification = classification
    indicator.scope = scope
    indicator.measurement = measurement
    indicator.record_status = choices.PUBLISHED
    indicator.creator_id = creator_id
    indicator.save()

    if previous:
        previous.posterior_record = indicator
        previous.save()

    indicator.code = build_code(indicator)
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
        indicator.action.code or indicator.action.name,
        indicator.classification,
        indicator.practice.code or indicator.practice.name,
        indicator.scope,
        indicator.measurement,
        str(indicator.seq),
        indicator.created.isoformat()[:10]
    ]).lower()


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


def get_numbers_of_action_classification_and_practice(
        action, model, ranking_calculation,
        standard_attribute, alternative_attribute=None):
    """
    Faz a consulta em um dado modelo (`model`) pela `action`
    """
    selected_attribute = alternative_attribute or standard_attribute

    for row in get_classification_and_practice(model, action):
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
        infrastructure_results=None,
        event_results=None,
        policy_results=None,
        ):

    # cria uma instância de Indicator
    title = title.replace(
        "[LABEL]",
        f"{action} {data['classification']} {data['practice']}",
    )

    indicator = create_record(
        title=title,
        action=action,
        classification=data['classification'],
        practice=Practice.objects.get(name=data['practice']),
        scope=scope,
        measurement=measurement,
        creator_id=creator_id,
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


def delete():
    for item in Indicator.objects.all():
        try:
            item.delete()
        except Exception as e:
            print(e)
