import datetime
import math
from collections import OrderedDict

import pysolr
from django.conf import settings
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render
from django.template import loader

from indicator.models import Indicator
from indicator import choices as indicator_choices


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

    if indicator.measurement == indicator_choices.FREQUENCY:
        names = []
        values = []
        for item in indicator.computed['items']:
            value = item.get('count') or item.get("value")
            if item['name'] and value:
                names.append(item['name'])
                values.append(value)

        return render(request, 'indicator_detail.html', {
            "object": indicator,
            "names": str(names),
            "values": str(values),
        })

    if indicator.measurement == indicator_choices.EVOLUTION:
        return render(request, 'indicator_detail.html', {
            "object": indicator,
            "source": str(_get_source_for_evolution_graphic(indicator.computed)),
            "series": str(_get_series_for_evolution_graphic_one(indicator.computed)),
        })


def _get_series_for_evolution_graphic_one(data):
    """
    [{ type: 'bar' }, { type: 'bar' }, { type: 'bar' }]
    """
    categories = data.get("categories") or data.get("subcategories")
    return "".join([
        "[",
        ", ".join(len(categories) * ["{ type: 'bar' }"]),
        "]"
    ])


def _get_series_for_evolution_graphic_two(data):
    """
    [
    // These series are in the first grid.
    { type: 'bar', seriesLayoutBy: 'row' },
    { type: 'bar', seriesLayoutBy: 'row' },
    { type: 'bar', seriesLayoutBy: 'row' },
    // These series are in the second grid.
    { type: 'bar', xAxisIndex: 1, yAxisIndex: 1 },
    { type: 'bar', xAxisIndex: 1, yAxisIndex: 1 },
    { type: 'bar', xAxisIndex: 1, yAxisIndex: 1 },
    { type: 'bar', xAxisIndex: 1, yAxisIndex: 1 }
    ]
    """
    categories = data.get("categories") or data.get("subcategories")
    return "".join([
        "[",
        _get_category_series_for_evolution_graphic(len(categories)),
        ",",
        _get_year_series_for_evolution_graphic(len(data['years'])),
        "]"
    ])

def _get_category_series_for_evolution_graphic(n):
    return ", ".join(
        n * ["{ type: 'bar', seriesLayoutBy: 'row' }"]
    )


def _get_year_series_for_evolution_graphic(n):
    return ", ".join(
        n * ["{ type: 'bar', xAxisIndex: 1, yAxisIndex: 1 }"]
    )


def _get_source_for_evolution_graphic(data):
    """
    [
      ['product', '2012', '2013', '2014', '2015'],
      ['Matcha Latte', 41.1, 30.4, 65.1, 53.3],
      ['Milk Tea', 86.5, 92.1, 85.7, 83.1],
      ['Cheese Cocoa', 24.1, 67.2, 79.5, 86.4]
    ]
    """
    categories = data.get("categories") or data.get("subcategories")
    name_and_years = ["observation"] + [str(y) for y in data['years']]
    items = [name_and_years]
    for cat in categories:
        item = [cat['name']] + cat['counts']
        items.append(item)
    return items


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
