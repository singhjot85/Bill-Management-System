from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.models import Session
from django.db.models import QuerySet

from project_apps.tenants.models import OrganizationDomain, OrganizationTenant, OrganizationBranding
from project_apps.utils.admin_utils import public_admin_site

User = get_user_model()


class OrganizationTenantAdmin(admin.ModelAdmin):

    # list_filter = ["is_removed"] TODO: Expose Removed Orgs also
    list_display = ["id", "name", "schema_name", "get_domains", "created", "modified"]
    ordering = ["-name", "-schema_name", "-modified", "-id"]
    readonly_fields = ["schema_name", "get_domains", "is_removed", "created", "modified"]

    fieldsets = (
        (None, {"fields": (("name", "schema_name"), "get_domains"), "classes": ["wide"]}),
        ("Meta", {"fields": (("created", "modified"), "is_removed")}),
    )

    actions = ["soft_delete_selected_schemas"]

    def get_queryset(self, request):
        qs = self.model.available_objects.prefetch_related("domains").all()

        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def get_domains(self, obj):
        return ", ".join([d.domain for d in obj.domains.all()])

    def soft_delete_selected_schema(self, request, queryset: QuerySet[OrganizationTenant]):
        try:
            for q in queryset:
                q.delete()
        except Exception as e:
            self.message_user(request, message=str(e), level=messages.ERROR)
            return

        self.message_user(request, message="Users Deleted Successfully", level=messages.INFO)

    get_domains.short_description = "Domains"


class OrgDomainAdmin(admin.ModelAdmin):

    list_filter = ["is_primary", "is_removed"]
    list_display = ["id", "domain", "is_primary", "is_removed"]
    ordering = ["-tenant", "-domain", "-id"]
    readonly_fields = ["is_removed"]

    actions = ["soft_delete_selected_schemas"]

    def soft_delete_selected_schema(self, request, queryset: QuerySet[OrganizationDomain]):
        try:
            for q in queryset:
                q.delete()
        except Exception as e:
            self.message_user(request, message=str(e), level=messages.ERROR)
            return

        self.message_user(request, message="Domains deleted successfully", level=messages.INFO)


class OrgBrandingAdmin(admin.ModelAdmin):

    list_filter = ["organization"]
    list_display = ["id", "organization", "country", "is_removed", "created", "modified"]
    ordering = ["organization", "country"]
    readonly_fields = ["is_removed"]

    fieldsets = (
        (None, {"fields": [("organization", "country"), ("phone", "email")], "classes": ["wide"]}),
        ("Navbar", {"fields": ["navbar_icon", "navbar_title"], "classes": ["wide"]}),
        ("Footer", {"fields": ["footer_icon", "footer_text", "footer_extra_text"], "classes": ["wide"]}),
    )

public_admin_site.register(OrganizationBranding, OrgBrandingAdmin)
public_admin_site.register(OrganizationDomain, OrgDomainAdmin)
public_admin_site.register(OrganizationTenant, OrganizationTenantAdmin)
public_admin_site.register(Group, GroupAdmin)
public_admin_site.register(ContentType)
public_admin_site.register(Session)
public_admin_site.register(User, UserAdmin)