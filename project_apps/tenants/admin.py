from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin

from project_apps.tenants.models import TenantConfigurations
from project_apps.utils.admin_utils import public_admin_site

User = get_user_model()

def get_config_path():
    return {
        "ui_configuration.json": "config/fixtures/ui/ui_configuration.json"
    }

class TenantConfigurationAdmin(admin.ModelAdmin):
    list_display = ["id", "interface_type", "version"]

    actions = [
        "seed_from_fixture"
    ]

    def seed_from_fixture(self, request, queryset):

        for obj in queryset:
            obj.details = get_config_path()[obj.interface_type]
            obj.save(update_fields=['details'])


public_admin_site.register(User, UserAdmin)
public_admin_site.register(TenantConfigurations, TenantConfigurationAdmin)
# TODO: Expose other default django models also.
