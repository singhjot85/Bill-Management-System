from django.conf import settings
from django.db import connection
from django_tenants.utils import get_public_schema_name

from apps.tenants.models import OrganizationTenant


def test_database_setup():
    public_tenant_qs = OrganizationTenant.objects.filter(schema_name=get_public_schema_name())
    private_tenant_qs = OrganizationTenant.objects.filter(schema_name=settings.TENANT_SCHEMA_NAME)

    assert public_tenant_qs.exists(), "Public Schema not created, verify test databse setup."
    assert private_tenant_qs.exists(), "Private Schema not created, verify test databse setup."

    assert (
        connection.schema_name == settings.TENANT_SCHEMA_NAME
    ), "Current schema is not correct, it should be private schema"
