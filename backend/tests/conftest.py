from typing import TYPE_CHECKING

import pytest
from django.conf import settings
from django_tenants.test.client import TenantClient
from django_tenants.utils import (
    get_public_schema_name,
    get_tenant_domain_model,
    get_tenant_model,
    schema_context,
)

if TYPE_CHECKING:
    from apps.tenants.models import OrganizationDomain, OrganizationTenant


TEST_SCHEMA = settings.TENANT_SCHEMA_NAME


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """
    Hooks into pytest-django's database setup to ensure the test tenant
    is created (and its schema migrated) exactly once per test session.
    """
    with django_db_blocker.unblock():
        Tenant: "OrganizationTenant" = get_tenant_model()
        Domain: "OrganizationDomain" = get_tenant_domain_model()

        tenant, created = Tenant.objects.get_or_create(
            schema_name=TEST_SCHEMA, defaults={"name": TEST_SCHEMA.replace("_", " ").title()}
        )

        if created:
            Domain.objects.get_or_create(domain="test.localhost", tenant=tenant, defaults={"is_primary": True})


@pytest.fixture
def tenant(db):
    """
    Fetches the pre-created test tenant for use in tests.
    """
    return get_tenant_model().objects.get(schema_name=TEST_SCHEMA)


@pytest.fixture(autouse=True)
def tenant_db(db, tenant):
    """
    Automatically activates the tenant schema context for ALL tests.
    Requires the 'db' fixture, ensuring DB access is enabled globally.
    """
    with schema_context(tenant.schema_name):
        yield


@pytest.fixture
def public_db(db):
    """
    Context manager that activates the public schema.
    Call this explicitly in tests that require the public database.
    """
    with schema_context(get_public_schema_name()):
        yield


@pytest.fixture
def tenant_client(tenant):
    """
    Provides a Django test client automatically configured for the test tenant.
    """
    return TenantClient(tenant)
