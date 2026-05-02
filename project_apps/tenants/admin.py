from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from django.forms import ModelForm, fields

from project_apps.utils.admin_utils import public_admin_site
from project_apps.tenants.models import OrganizationTenant, OrganizationDomain

User = get_user_model()


class OrganizationTenantAdmin(admin.ModelAdmin):
    
    list_filter = ["is_removed"]
    list_display = ["id", "name", "schema_name", "get_domains", "created", "modified"]
    ordering = ["-name", "-schema_name", "-modified", "-id"]
    readonly_fields = ["get_domains"]

    fieldsets = (
        (
            None, {
                "fields": ('id', ("name", "schema_name"), "get_domains"),
                "classes": ["wide"]
            }
        ),
        (
            "Meta", {
                "fields": (("created", "modified"), "is_removed")
            }
        )
    )

    def get_queryset(self, request):
        qs = self.model._default_manager.prefetch_related("domains").get_queryset()
        
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def get_domains(self, obj):
        return ", ".join([d.domain for d in obj.domains.all()])[1:]

    get_domains.short_description = "Domains"


public_admin_site.register(OrganizationTenant, OrganizationTenantAdmin)
public_admin_site.register(User, UserAdmin)