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


def run():
    # generate_institutions_indicators()
    # generate_geographical_indicators()
    # controller.generate_scientific_production_institutions_ranking(1)
    controller.generate_non_standard_affiliation_scientific_production_evolution(1)

