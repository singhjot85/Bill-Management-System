from django.db import connection, models
from django_tenants.models import DomainMixin, TenantMixin

from apps.tenants.constants import CountryChoices
from utils import SafeModelMixin, VersionedBetterModelMixin


class OrganizationTenant(SafeModelMixin, TenantMixin):
    """Tenant model required for Django Tenants."""

    name = models.CharField(verbose_name="Tenant Name", max_length=255, null=False, blank=False)
    in_production = models.BooleanField(default=False, blank=True, null=True)

    def __str__(self):
        return self.name


class OrganizationDomain(SafeModelMixin, DomainMixin):
    """Domain Model required fot Django Tenants."""

    pass


class OrganizationBranding(VersionedBetterModelMixin):

    organization = models.OneToOneField(to=OrganizationTenant, on_delete=models.PROTECT)

    country = models.CharField(
        verbose_name="Organization Country",
        max_length=125,
        choices=CountryChoices.choices,
        default=CountryChoices.INDIA.value,
    )
    phone = models.CharField(verbose_name="Organization Phone", max_length=10, null=True, blank=True)
    email = models.CharField(verbose_name="Organization Email", null=True, blank=True)

    navbar_icon = models.CharField(max_length=100, null=True, blank=True)
    navbar_title = models.CharField(max_length=100, null=True, blank=True)

    footer_icon = models.CharField(verbose_name="Footer Icon(s) before Text", max_length=255, null=True, blank=True)
    footer_text = models.TextField(verbose_name="Text in Footer Section", null=True, blank=True)
    footer_extra_text = models.TextField(verbose_name="Extra Text at end of footer", null=True, blank=True)

    @classmethod
    def get_current_branding(cls):
        return cls.objects.filter(organization__schema_name=connection.schema_name).order_by(cls.DEFAULT_ORDERING)
