import logging
from django.db.models import Count, Sum
from django.contrib.auth import get_user_model

from .models import ScholarlyArticles, Journals, Affiliations


User = get_user_model()


def affiliations_numbers():
    stats = {}
    stats['total'] = Affiliations.objects.count()
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

    stats['official'] = official.count()
    stats['official__city'] = official__city.count()
    stats['official__state'] = official__state.count()
    stats['official__country'] = official__country.count()
    stats['official__country__BR'] = official__country__BR.count()
    stats['country'] = Affiliations.objects.filter(
        country__isnull=False,
    ).count()
    stats['country__BR'] = Affiliations.objects.filter(
        country__acron2='BR',
    ).count()
    return {
        "items": [
            {"name": k, "count": v}
            for k, v in stats.items()
        ]
    }


def articles_numbers(
        open_access_status_items=None,
        oa_status_flag=False,
        use_license_flag=False,
        publisher_institution_type_flag=False,
        thematic_areas_flag=False,
        publisher_UF_flag=False,
        ppgs_flag=False,
        ):
    values_parameters = _get_values_parameters(
        oa_status_flag,
        use_license_flag,
        publisher_institution_type_flag,
        thematic_areas_flag,
        publisher_UF_flag,
        ppgs_flag,
    )
    open_access_status_items = (
        open_access_status_items or ['gold', 'bronze', 'green', 'hybrid']
    )
    oa_articles = ScholarlyArticles.objects.filter(
        open_access_status__in=open_access_status_items
    )
    summarized = oa_articles.values(
        *values_parameters
    )
    annotated = summarized.annotate(
        count=Count('id', distinct=True)
    )
    items = annotated.order_by('count').iterator()
    for item in items:
        item.update({
            "total": oa_articles.count(),
        })
        yield item


def _get_values_parameters(
        oa_status_flag=False,
        use_license_flag=False,
        publisher_institution_type_flag=False,
        thematic_areas_flag=False,
        publisher_UF_flag=False,
        ppgs_flag=False,
        ):
    values_parameters = []
    if oa_status_flag:
        values_parameters.append('open_access_status')
    if use_license_flag:
        values_parameters.append('use_license')
    if ppgs_flag:
        values_parameters.extend([
            'contributors__affiliation__official__name',
            'contributors__affiliation__official__level_1',
            'contributors__affiliation__official__level_2',
            'contributors__affiliation__official__level_3',
            'contributors__affiliation__official__location__city__name',
            'contributors__affiliation__official__location__state__acronym',
        ])

    if thematic_areas_flag:
        raise NotImplementedError(
            "Unable to generate indicators by thematic areas"
        )
        values_parameters.append('thematic_areas')

    if publisher_UF_flag:
        raise NotImplementedError(
            "Unable to generate indicators by publisher UF"
        )
        values_parameters.append('publisher__location__state__acronym')

    if publisher_institution_type_flag:
        raise NotImplementedError(
            "Unable to generate indicators by publisher UF"
        )
        values_parameters.append('publisher')
    return values_parameters


def journals_numbers(
        oa_status_flag=False,
        use_license_flag=False,
        publisher_institution_type_flag=False,
        thematic_areas_flag=False,
        publisher_UF_flag=False,
        ppgs_flag=False,
        ):
    values_parameters = []
    if oa_status_flag:
        values_parameters.append('open_access_status')
        journal_or_id = "journal"
    if use_license_flag:
        values_parameters.append('use_license')
        journal_or_id = "journal"
    if ppgs_flag:
        # dados ausentes
        journal_or_id = "journal"
        raise NotImplementedError(
            "Unable to generate journals indicator by PPGs"
        )
        values_parameters.extend([
            'contributors__affiliation__official__name',
            'contributors__affiliation__official__level_1',
            'contributors__affiliation__official__level_2',
            'contributors__affiliation__official__level_3',
            'contributors__affiliation__official__location__city__name',
            'contributors__affiliation__official__location__state__acronym',
        ])

    if thematic_areas_flag:
        # dados ausentes
        journal_or_id = "id"
        raise NotImplementedError(
            "Unable to generate journals indicator by thematic areas"
        )
        values_parameters.append('thematic_areas')
    if publisher_UF_flag:
        # dados ausentes
        journal_or_id = "id"
        raise NotImplementedError(
            "Unable to generate journals indicator by publisher UF"
        )
        values_parameters.append('publisher__location__state__acronym')
    if publisher_institution_type_flag:
        # FIXME tornar publisher do tipo Institution
        # values_parameters.append('publisher__institution_type')
        journal_or_id = "id"
        values_parameters.append('publisher')

    if oa_status_flag or use_license_flag or ppgs_flag:
        model = ScholarlyArticles
    else:
        model = Journals

    # if journal_or_id == "id":
    #     values_parameters.extend([
    #         'journal__journal_name',
    #         'journal__journal_issn_l',
    #         'journal__journal_issns',
    #     ])
    filtered = model.objects.filter(
        open_access_status__in=['gold', 'bronze', 'green', 'hybrid']
    )
    logging.info("Model: %s" % model)
    logging.info("Model count: %s" % model.objects.count())
    logging.info("parametro de Count(): %s" % journal_or_id)
    logging.info("values_parameters: %s" % values_parameters)

    filtered_total = filtered.values(
            journal_or_id
        ).annotate(
            count=Count(journal_or_id, distinct=True)
        ).count()

    logging.info("filtered_total: %s" % filtered_total)

    annotated = filtered.values(
            *values_parameters
        ).annotate(
            count=Count(journal_or_id, distinct=True)
        )
    logging.info(
        "annotated = filtered.values(*values_parameters).annotate(count=Count(journal_or_id, distinct=True): %s" % annotated)

    logging.info("annotated.count(): %s" % annotated.count())

    items = annotated.order_by('count').iterator()
    for item in items:
        item.update({
            "total": filtered.count(),
        })
        logging.info(item)
        yield item
