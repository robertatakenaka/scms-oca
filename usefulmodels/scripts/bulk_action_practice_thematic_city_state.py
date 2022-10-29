from django.contrib.auth import get_user_model
from . import (
    bulk_action,
    bulk_practice,
    bulk_themaitic,
    bulk_cities,
    bulk_sates,
)

User = get_user_model()

# This script add bulk of actions
# Consider that existe a user with id=1

SEPARATOR = ';'


def run(*args):
    # bulk_action.run()
    # bulk_practice.run()
    bulk_thematic.run()
    bulk_cities.run()
    bulk_sates.run()
