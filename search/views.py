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
    layouts = ["bar-label-rotation", "categories_1_grid", "categories_2_grids"]
    try:
        indicator = Indicator.objects.get(
            pk=indicator_id, record_status='PUBLISHED')
    except Indicator.DoesNotExist:
        raise Http404("Indicator does not exist")

    try:
        cat1_name = indicator.computed['cat1_name']
        data = _get_matrix(indicator.computed)
        graphic_type = layouts[int(request.GET.get('g') or 2)]
        if graphic_type == "bar-label-rotation":
            label_options = _get_series(
                _get_texts_label_labelOption(len(data['cat2_values'])))
            cat2_name_and_values_list = _name_and_values_by_category(**data)
            cat2_data = _get_cat2_text(cat2_name_and_values_list)
            params = {
                "label_options": label_options,
                "cat2_values": data['cat2_values'],
                "cat1_values": data['cat1_values'],
                "cat2_data": cat2_data,
            }
        else:
            rows = _format_data_as_table(cat1_name, **data)
            if graphic_type == "categories_1_grid":
                texts = _get_texts_for_1_grid(len(data['cat1_values']))
            else:
                texts = _get_texts_for_2_grids(
                    len(data['cat1_values']), len(data['cat2_values']))
            series = _get_series(texts)
            params = {
                "source": str(rows),
                "series": series,
            }
        params.update({
            "graphic_type": graphic_type,
            "object": indicator,
        })

        return render(request, 'indicator/indicator_detail.html', params)
    except KeyError:
        names = []
        values = []
        for item in indicator.computed['items']:
            value = item.get('count') or item.get("value")
            if item['name'] and value:
                names.append(item['name'])
                values.append(value)

        return render(request, 'indicator/indicator_detail.html', {
            "graphic_type": "",
            "object": indicator,
            "names": str(names),
            "values": str(values),
            "graphic_height": min([len(names) * 20, 30000]),
        })


def _get_matrix(summarized):
    items = summarized['items']
    cat1_name = summarized['cat1_name']
    cat2_name = summarized['cat2_name']
    cat1_values = summarized.get("cat1_values") or []
    cat2_values = []
    matrix = {}
    for item in items:
        if item[cat1_name] not in cat1_values:
            cat1_values.append(str(item[cat1_name]))
        if item[cat2_name] not in cat2_values:
            cat2_values.append(str(item[cat2_name]))
        key = (item[cat1_name], item[cat2_name])
        matrix[key] = item['count']
    return dict(
        cat1_values=cat1_values,
        cat2_values=cat2_values,
        matrix=matrix,
    )


def _name_and_values_by_category(matrix, cat1_values, cat2_values):
    items = []
    for cat2_value in cat2_values:
        cat_name = cat2_value
        cat_values = []
        for c1_value in cat1_values:
            key = (c1_value, cat2_value)
            cat_values.append(matrix.get(key) or 0)
        items.append((cat_name, cat_values))
    return items


def _format_data_as_table(cat1_name, matrix, cat1_values, cat2_values):
    """
    Ex.1
        cat1_name = "year"
        cat2_name = "open_access_status"

    Ex.2
        cat1_name = "practice__name"
        cat2_name = "classification"
    """
    rows = [
        [cat1_name] + cat1_values,
    ]
    for c2_value in cat2_values:
        row = [c2_value]
        for c1_value in cat1_values:
            key = (c1_value, c2_value)
            row.append(matrix.get(key) or 0)
        rows.append(row)
    return rows


def _get_series(n_and_text_tuples):
    texts = []
    for n, text in n_and_text_tuples:
        texts.extend(n * [text])
    return f"[{', '.join(texts)}]"


def _get_texts_for_2_grids(cat1_len, cat2_len):
    return [
        (cat2_len, "{ type: 'bar', seriesLayoutBy: 'row' }"),
        (cat1_len, "{ type: 'bar', xAxisIndex: 1, yAxisIndex: 1 }"),
    ]


def _get_texts_for_1_grid(cat1_len):
    return [
        (cat1_len, "{ type: 'bar' }"),
    ]


def _get_texts_label_labelOption(cat1_len):
    return [
        (cat1_len, "{ label: labelOption }"),
    ]


def _get_cat2_text(cat2_name_and_values_list):
    text = (
        """
        {
            name: '%s', type: 'bar', barGap: 0, label: labelOption,
            emphasis: {
                focus: 'series'
            },
            data: %s
        }
        """
    )
    items = []
    for name, values in cat2_name_and_values_list:
        items.append(
            text % (name, str(values))
        )
    return f"[{', '.join(items)}]"


def indicator_computed(request, indicator_id):
    try:
        indicator = Indicator.objects.get(
            pk=indicator_id, record_status='PUBLISHED')
    except Indicator.DoesNotExist:
        raise Http404("Indicator does not exist")
    return render(request, 'indicator/indicator_computed.html', {"object": indicator})


def indicator_dataset(request, indicator_id):
    try:
        indicator = Indicator.objects.get(
            pk=indicator_id, record_status='PUBLISHED')
    except Indicator.DoesNotExist:
        raise Http404("Indicator does not exist")
    return render(request, 'indicator/indicator_dataset.html', {"object": indicator})
