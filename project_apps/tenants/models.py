from django.db import models
from django_tenants.models import DomainMixin, TenantMixin

from project_apps.utils import SafeModelMixin


class OrganizationTenant(TenantMixin, SafeModelMixin):
    """Tenant model required for Django Tenants."""

    name = models.CharField(verbose_name="Tenant Name", max_length=255, null=False, blank=False)

    def __str__(self):
        return self.name


class OrganizatinDomain(DomainMixin):
    """Domain Model required fot Django Tenants."""

    pass
