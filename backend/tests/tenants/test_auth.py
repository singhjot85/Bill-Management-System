import pytest
from django.contrib.auth.models import User
from django_tenants.test.client import TenantClient
from django_tenants.utils import get_public_schema_name, schema_context
from rest_framework import status
from rest_framework.authtoken.models import Token

from apps.tenants.models import OrganizationDomain


@pytest.mark.django_db
def test_token_authentication_flow(tenant, settings):
    # Enable all hosts for tests
    settings.ALLOWED_HOSTS = ["*"]

    # 1. Create primary domain for the tenant in the public schema
    with schema_context(get_public_schema_name()):
        OrganizationDomain.objects.get_or_create(tenant=tenant, domain="test.localhost", defaults={"is_primary": True})
        tenant.refresh_from_db()

    # 2. Instantiate TenantClient AFTER creating the domain and refreshing tenant
    client = TenantClient(tenant)

    # 3. Create user and token
    user = User.objects.create_user(username="testuser", password="password123", email="test@bma.com")
    token = Token.objects.create(user=user)

    # 4. Test API call without token
    url = "/api/auth/user/"
    response = client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # 5. Test API call with token
    response = client.get(url, HTTP_AUTHORIZATION=f"Token {token.key}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "testuser"
