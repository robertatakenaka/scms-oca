from django.urls import include, path
from django.http import HttpResponseRedirect
from django.utils.translation import gettext as _

from wagtail.core import hooks
from wagtail.contrib.modeladmin.views import CreateView, EditView
from wagtail.contrib.modeladmin.options import (ModelAdmin, modeladmin_register, ModelAdminGroup)

from .models import (Indicator,)


class IndicatorDirectoryEditView(EditView):

    def form_valid(self, form):
        self.object = form.save_all(self.request.user)
        return HttpResponseRedirect(self.get_success_url())


class IndicatorDirectoryCreateView(CreateView):

    def form_valid(self, form):
        self.object = form.save_all(self.request.user)
        return HttpResponseRedirect(self.get_success_url())


class IndicatorAdmin(ModelAdmin):
    model = Indicator
    ordering = ('-updated',)
    create_view_class = IndicatorDirectoryCreateView
    edit_view_class = IndicatorDirectoryEditView
    menu_label = _('Indicator')  # ditch this to use verbose_name_plural from model
    menu_icon = 'folder-open-inverse'  # change as required
    menu_order = 100  # will put in 3rd place (000 being 1st, 100 2nd)
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = False  # or True to exclude pages of this type from Wagtail's explorer view
    inspect_view_enabled = True

    list_display = (
        'title',
        'record_status',
        'validity',
        'total',
        'updated',
    )

    list_filter = (
        'action_and_practice__action__name',
        'action_and_practice__classification',
        'action_and_practice__practice__name',
        'record_status',
        'validity',
        'total',
        'scope',
        'measurement',
        'scientific_production__communication_object',
        'scientific_production__open_access_status',
        'scientific_production__use_license',
        'scientific_production__apc',
        )

    search_fields = (
        'title',
        'action_and_practice__action__name',
        'action_and_practice__classification',
        'action_and_practice__practice__name',
    )


modeladmin_register(IndicatorAdmin)


@hooks.register('register_admin_urls')
def register_disclosure_url():
    return [
        path('indicator/',
        include('indicator.urls', namespace='indicator')),
    ]
