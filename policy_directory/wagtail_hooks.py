from django.urls import include, path
from django.utils.translation import gettext as _
from wagtail import hooks
from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    ModelAdminGroup,
    modeladmin_register,
)

from . import views
from .button_helper import PolicyDirectoryHelper
from .models import PolicyDirectory, PolicyDirectoryFile


class PolicyDirectoryAdmin(ModelAdmin):
    model = PolicyDirectory
    ordering = ("-updated",)
    create_view_class = views.PolicyDirectoryCreateView
    edit_view_class = views.PolicyDirectoryEditView
    menu_label = _("Policy Directory")
    menu_icon = "folder"
    menu_order = 100
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = (
        False  # or True to exclude pages of this type from Wagtail's explorer view
    )
    list_display = ("title", "link", "record_status", "description", "creator", "updated", "created")
    list_filter = ("practice", "classification", "thematic_areas", "record_status")
    search_fields = ("title", "description")
    list_export = ("title", "link", "description")
    export_filename = "policy_directory"

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # If the user is not a staff
        if not request.user.is_staff:
            # Only show the records create by the current user
            return qs.filter(creator=request.user)
        else: 
            return qs


class PolicyDirectoryFileAdmin(ModelAdmin):
    model = PolicyDirectoryFile
    ordering = ("-updated",)
    create_view_class = views.PolicyDirectoryFileCreateView
    button_helper_class = PolicyDirectoryHelper
    menu_label = _("Policy Directory Upload")
    menu_icon = "folder"
    menu_order = 200
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = (
        "attachment",
        "line_count",
        "is_valid",
        "creator",
        "updated",
        "created",
    )
    list_filter = ("is_valid",)
    search_fields = ("attachment",)


class PolicyDirectoryAdminGroup(ModelAdminGroup):
    menu_label = _("Policy Directory")
    menu_icon = "folder-open-inverse"
    menu_order = 200
    items = (
        PolicyDirectoryAdmin,
        PolicyDirectoryFileAdmin,
    )


modeladmin_register(PolicyDirectoryAdminGroup)


@hooks.register("register_admin_urls")
def register_policy_url():
    return [
        path(
            "policy_directory/PolicyDirectoryfile/",
            include("policy_directory.urls", namespace="policy_directory"),
        ),
    ]
