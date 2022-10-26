import json
import datetime
import math
from collections import OrderedDict

import pysolr
from django.conf import settings
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render
from django.template import loader

from indicator.models import Indicator


solr = pysolr.Solr(settings.HAYSTACK_CONNECTIONS["default"]["URL"],
                   timeout=settings.HAYSTACK_CONNECTIONS["default"]["SOLR_TIMEOUT"])


def search(request):
    fqs = []
    filters = {}
    search_query = request.GET.get('q', None)
    search_field = request.GET.get('search-field', None)
    fqfilters = request.GET.get('filters', None)
    facet_name = request.GET.get('more_facet_name', None)
    facet_count = request.GET.get('more_facet_count', None)
    sort_by = request.GET.get('selectSortKey', 'score asc')

    if search_query == "" or not search_query:
        search_query = "*:*"

    if search_field:
        search_query = search_field

    # Page
    try:
        page = abs(int(request.GET.get('page', 1)))
    except (TypeError, ValueError):
        return Http404("Not a valid number for page.")

    rows = int(request.GET.get('itensPage', settings.SEARCH_PAGINATION_ITEMS_PER_PAGE))

    start_offset = (page - 1) * rows

    filters['start'] = start_offset
    filters['rows'] = rows

    if facet_name and facet_count:
        filters['f.' + facet_name + '.facet.limit'] = facet_count

    if fqfilters:
        fqs = fqfilters.split(',')

    fqs = ['%s:"%s"' % (fq.split(":")[0], fq.split(":")[1]) for fq in fqs]

    # fqs.append('status:"Ativo"')

    # Adiciona o Solr na pesquisa
    search_results = solr.search(search_query, fq=fqs, sort=sort_by, **filters)

    # Cria um dicionário ordenado dos facets considerando a lista settings.SEARCH_FACET_LIST
    facets = search_results.facets['facet_fields']
    ordered_facets = OrderedDict()

    for facet in settings.SEARCH_FACET_LIST:
        ordered_facets[facet] = facets.get(facet, "")

    if request.GET.get('raw'):
        return JsonResponse(search_results.raw_response, safe=False)

    wt = request.GET.get('wt')
    if wt == 'csv':
        filename = "%s_%s.csv" % ("download_csv_", datetime.datetime.today().strftime("%d_%m_%Y"))

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s"' % (filename)

        t = loader.get_template('csv_template.txt')
        c = {'search_results': search_results}
        response.write(t.render(c))
        return response

    total_pages = int(math.ceil(float(search_results.hits) / rows))

    return render(request, 'search.html', {
        'search_query': '' if search_query == "*:*" else search_query,
        'search_results': search_results,
        'facets': ordered_facets,
        'page': page,
        'fqfilters': fqfilters if fqfilters else "",
        'start_offset': start_offset,
        'itensPage': rows,
        'wt': wt if wt else "HTML",
        'settings': settings,
        'total_pages': total_pages,
        'selectSortKey': sort_by
    })


def indicator_detail(request, indicator_id):
    try:
        indicator = Indicator.objects.get(
            pk=indicator_id, record_status='PUBLISHED')
    except Indicator.DoesNotExist:
        raise Http404("Indicator does not exist")

    names = [item['name'] for item in indicator.computed['items']]
    values = [item['count'] for item in indicator.computed['items']]

    return render(request, 'indicator_detail.html', {
        "object": indicator,
        "names": str(names),
        "values": str(values),
    })


def indicator_computed(request, indicator_id):
    try:
        indicator = Indicator.objects.get(
            pk=indicator_id, record_status='PUBLISHED')
    except Indicator.DoesNotExist:
        raise Http404("Indicator does not exist")
    return render(request, 'indicator_computed.html', {"object": indicator})


def indicator_dataset(request, indicator_id):
    try:
        indicator = Indicator.objects.get(
            pk=indicator_id, record_status='PUBLISHED')
    except Indicator.DoesNotExist:
        raise Http404("Indicator does not exist")
    return render(request, 'indicator_dataset.html', {"object": indicator})
