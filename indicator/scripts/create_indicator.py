from indicator import controller
from institution.models import Institution
from usefulmodels.models import Action

# def run():
#     for institution in Institution.objects.all():

#     indicator = controller.generate_indicator(
#         institution="Universidade de São Paulo",
#         practice="literatura em acesso aberto",
#         action=None,
#         classification=None,
#         thematic_area=None,
#         start_date=None,
#         end_date=None,
#         location=None,
#         return_data=True,
#         return_rows=True,
#     )

#     indicator.creator_id = 1
#     indicator.save()


def generate_institutions_indicators():
    creator_id = 1
    for action in Action.objects.all():
        print(action)
        title = "Número de [LABEL] por instituição"
        controller.number_of_action_classification_and_practice_by_institution(
            title, action, creator_id)


def generate_geographical_indicators():
    creator_id = 1
    for action in Action.objects.all():
        title = "Número de [LABEL] por estado"
        controller.number_of_action_classification_and_practice_by_state(
            title, action, creator_id)


def generate_open_access_status_evolution(creator_id):
    controller.generate_open_access_status_evolution(
        creator_id=creator_id,
        years=None,
        BR_affiliations=False,
        oa_status_items=None,
    )
    for oa_status in ('gold', 'bronze', 'green', 'hybrid', ):
        controller.generate_open_access_status_evolution(
            creator_id=creator_id,
            years=None,
            BR_affiliations=False,
            oa_status_items=[oa_status],
        )


def generate_scientific_production_ranking(creator_id):
    # controller.scientific_production_institutions_ranking(
    #     creator_id=creator_id,
    #     oa_status_items=None,
    #     years=None,
    #     BR_affiliations=False,
    # )
    # for oa_status in ('gold', 'bronze', 'green', 'hybrid', ):
    #     controller.scientific_production_institutions_ranking(
    #         creator_id=creator_id,
    #         oa_status_items=[oa_status],
    #         years=None,
    #         BR_affiliations=False,
    #     )
    for year in controller.get_years_range(10):
        controller.scientific_production_institutions_ranking(
            creator_id=creator_id,
            oa_status_items=None,
            years=[year],
            BR_affiliations=False,
        )
        for oa_status in ('gold', 'bronze', 'green', 'hybrid', ):
            controller.scientific_production_institutions_ranking(
                creator_id=creator_id,
                oa_status_items=[oa_status],
                years=[year],
                BR_affiliations=False,
            )


def number_of_journals(creator_id):
    controller.number_of_journals(
        creator_id,
        oa_status_flag=True,
        use_license_flag=False,
        publisher_institution_type_flag=False,
        thematic_areas_flag=False,
        publisher_UF_flag=False,
        ppgs_flag=False,
    )
    controller.number_of_journals(
        creator_id,
        oa_status_flag=False,
        use_license_flag=True,
        publisher_institution_type_flag=False,
        thematic_areas_flag=False,
        publisher_UF_flag=False,
        ppgs_flag=False,
    )


def run():
    # controller.delete()
    # controller.number_of_actions(1)
    # controller.number_of_actions_with_practice(1)
    # generate_open_access_status_evolution(1)

    # # generate_institutions_indicators()
    # # generate_geographical_indicators()
    # generate_scientific_production_ranking(creator_id=1)
    number_of_journals(creator_id=1)
