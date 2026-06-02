"""
Test factories using factory-boy.
"""

import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory

from apps.customer_management.models import Customer
from apps.tenants.models import (
    OrganizationBranding,
    OrganizationDomain,
    OrganizationTenant,
)

User = get_user_model()


class UserFactory(DjangoModelFactory):

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@test.com")
    password = factory.PostGenerationMethodCall("set_password", "qwerty@123")

    is_active = True
    is_staff = False

    class Meta:
        model = User


class OrganizationTenantFactory(DjangoModelFactory):

    name = factory.Sequence(lambda n: f"org_{n}")

    class Meta:
        model = OrganizationTenant


class OrganizationDomainFactory(DjangoModelFactory):

    class Meta:
        model = OrganizationDomain


class OrganizationBrandingFactory(DjangoModelFactory):

    organization = factory.SubFactory(OrganizationTenantFactory)

    class Meta:
        model = OrganizationBranding


class CustomerFactory(DjangoModelFactory):

    class Meta:
        model = Customer
