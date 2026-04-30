from django.db import models
from django.core.serializers.json import DjangoJSONEncoder
from django_tenants.models import DomainMixin, TenantMixin

from project_apps.utils import SafeModelMixin, VersionedBetterModelMixin
from project_apps.tenants.constants import TenantConfigurationInterfaceChoices


class OrganizationTenant(TenantMixin, SafeModelMixin):
    """Tenant model required for Django Tenants."""

    name = models.CharField(verbose_name="Tenant Name", max_length=255, null=False, blank=False)

    def __str__(self):
        return self.name


class OrganizationDomain(DomainMixin):
    """Domain Model required fot Django Tenants."""

    pass


class TenantConfigurations(VersionedBetterModelMixin):

    interface_type = models.CharField(null=False, blank=False, choices=TenantConfigurationInterfaceChoices.choices)
    tenant = models.ForeignKey(to=OrganizationTenant, on_delete=models.PROTECT, null=False, blank=False)
    details = models.JSONField(default=dict, encoder=DjangoJSONEncoder, null=True, blank=True)