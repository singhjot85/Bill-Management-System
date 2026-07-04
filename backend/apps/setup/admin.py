from django.contrib import admin

from utils.admin_utils import private_admin_site, public_admin_site

from .models import Configurations


class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ["id", "interface_type", "version"]
    list_filter = ["interface_type"]
    readonly_fields = ["created", "modified", "id", "version", "is_removed"]

    fieldsets = (
        (
            None,
            {
                "fields": ["is_removed", ("interface_type", "version")],
            },
        ),
        ("Content", {"fields": ["details"], "classes": ["wide"]}),
    )


public_admin_site.register(Configurations, ConfigurationAdmin)
private_admin_site.register(Configurations, ConfigurationAdmin)
