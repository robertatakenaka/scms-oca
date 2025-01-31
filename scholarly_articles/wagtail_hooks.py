from django.utils.translation import gettext as _

from wagtail.contrib.modeladmin.options import (ModelAdmin, modeladmin_register)

from .models import (ScholarlyArticles, Contributors)


class ScholarlyArticlesAdmin(ModelAdmin):
    model = ScholarlyArticles
    menu_label = 'Scholarly Articles'  # ditch this to use verbose_name_plural from model
    menu_icon = 'folder'  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = False  # or True to exclude pages of this type from Wagtail's explorer view
    list_display = (
        'doi',
        'doi_url',
        'genre',
        'is_oa',
        'journal_is_in_doaj',
        'journal_issns',
        'journal_issn_l',
        'journal_name',
        'published_date',
        'publisher',
        'title',
        'article_json',
    )
    list_filter = ('journal_issn_l',)
    search_fields = ('doi', 'journal_issn_l')


class ContributorsAdmin(ModelAdmin):
    model = Contributors
    menu_label = 'Contributors'
    menu_icon = 'folder'
    menu_order = 300
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = False  # or True to exclude pages of this type from Wagtail's explorer view
    list_display = (
        'doi',
        'doi_url',
        'family',
        'given',
        'orcid',
        'authenticated_orcid',
        'affiliation',
    )
    list_filter = ('orcid',)
    search_fields = ('doi', 'orcid')


modeladmin_register(ScholarlyArticlesAdmin)
modeladmin_register(ContributorsAdmin)
