from indicator import controller
from institution.models import Institution
from usefulmodels.models import Action


PARAMETERS = {
    'OPEN_ACCESS_STATUS': {
        'title': 'tipo',
        'name': 'open_access_status',
        'category_attributes': ['open_access_status']},
    'USE_LICENSE': {
        'title': 'licença de uso',
        'name': 'use_license',
        'category_attributes': ['use_license']},
    'AFFILIATION_UF': {
        'title': 'UF',
        'name': 'contributors__affiliation__official__location__state__acronym',
        'category_attributes': [
            'contributors__affiliation__official__location__state__acronym']},
    'AFFILIATION': {
        'title': 'instituição',
        'name': 'institution',
        'category_attributes': [
            'contributors__affiliation__official__name',
            'contributors__affiliation__official__level_1',
            'contributors__affiliation__official__level_2',
            'contributors__affiliation__official__level_3',
            'contributors__affiliation__official__location__city__name',
            'contributors__affiliation__official__location__state__acronym']},
    'THEMATIC_AREA': {
        'name': 'área temática',
        'category_attributes': [
            'thematic_areas__level0',
            'thematic_areas__level1',
            'thematic_areas__level2']},
    'PUBLISHER_UF': {
        'title': 'instituição',
        'name': 'institution',
        'name': 'UF',
        'category_attributes': ['publisher__location__state__acronym']},
    'PUBLISHER': {
        'title': 'instituição',
        'name': 'institution',
        'category_attributes': [
            'publisher__name',
            'publisher__level_1',
            'publisher__level_2',
            'publisher__level_3',
            'publisher__location__city__name',
            'publisher__location__state__acronym']},
    'INSTITUTION': {
        'title': 'instituição',
        'name': 'institution',
        'category_attributes': [
            'institutions__name',
            'institutions__level_1',
            'institutions__level_2',
            'institutions__level_3',
            'institutions__location__city__name',
            'institutions__location__state__acronym']},
    'ORGANIZATION': {
        'title': 'instituição',
        'name': 'institution',
        'category_attributes': [
            'organization__name',
            'organization__level_1',
            'organization__level_2',
            'organization__level_3',
            'organization__location__city__name',
            'organization__location__state__acronym']},
}


def evolution_of_scientific_production(creator_id, years_number=5):
    # OK
    parameters = [
        'OPEN_ACCESS_STATUS',
        'USE_LICENSE',
        # 'THEMATIC_AREA',
    ]
    for param_name in parameters:
        controller.evolution_of_scientific_production(
            creator_id=creator_id,
            category_title=PARAMETERS[param_name]['title'],
            category_name=PARAMETERS[param_name]['name'],
            category_attributes=PARAMETERS[param_name]['category_attributes'],
            years_range=controller.get_years_range(years_number),
        )

    # FIXME
    parameters = [
        'AFFILIATION_UF',
        'AFFILIATION',
        # 'THEMATIC_AREA',
    ]
    for param_name in parameters:
        controller.evolution_of_scientific_production_for_larger_groups(
            creator_id=creator_id,
            category_title=PARAMETERS[param_name]['title'],
            category_name=PARAMETERS[param_name]['name'],
            category_attributes=PARAMETERS[param_name]['category_attributes'],
            years_range=controller.get_years_range(years_number),
        )


def journals_numbers(creator_id):
    # OK
    parameters = [
        'OPEN_ACCESS_STATUS',
        'USE_LICENSE',
        # 'PUBLISHER_UF',
        # 'PUBLISHER',
        # 'THEMATIC_AREA',
    ]
    for param_name in parameters:
        controller.journals_numbers(
            creator_id=creator_id,
            category_title=PARAMETERS[param_name]['title'],
            category_attributes=PARAMETERS[param_name]['category_attributes'],
        )


def actions_numbers(creator_id):
    # OK
    controller.actions_numbers(
        creator_id,
        category_title='',
        category_name='action',
        category_attributes=['action__name', 'classification'],
        category2_name=None,
        category2_attributes=None
    )
    # FIXME
    controller.actions_numbers(
        creator_id,
        category_title=" por prática",
        category_attributes=["practice__name"],
        category_name="practice__name",
        category2_name="action",
        category2_attributes=["action__name", "classification"]
    )
    # FIXME
    controller.actions_numbers(
        creator_id,
        category_title=" por área temática",
        category_attributes=[
            "thematic_areas__level0",
            "thematic_areas__level1",
            "thematic_areas__level2"],
        category_name="thematic_areas",
        category2_name="action__name",
        category2_attributes=["action__name", "classification"]
    )
    # controller.actions_numbers(
    #     creator_id,
    #     category_title=" por instituição",
    #     category_name='action__name',
    #     category_attributes=['action__name'] + [
    #         'institutions__name',
    #         'institutions__level_1',
    #         'institutions__level_2',
    #         'institutions__level_3',
    #         'institutions__location__city__name',
    #         'institutions__location__state__acronym'
    #     ] + [
    #         'organization__name',
    #         'organization__level_1',
    #         'organization__level_2',
    #         'organization__level_3',
    #         'organization__location__city__name',
    #         'organization__location__state__acronym'
    #     ]
    # )
    # controller.actions_numbers(
    #     creator_id,
    #     category_title=" por UF",
    #     category_name='action__name',
    #     category_attributes=['action__name'] + [
    #         'institutions__location__state__acronym'
    #     ] + [
    #         'organization__location__state__acronym'
    #     ]
    # )


def run():
    controller.delete()
    evolution_of_scientific_production(1)
    journals_numbers(creator_id=1)
    actions_numbers(1)
