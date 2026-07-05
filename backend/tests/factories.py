"""
Test factories using factory-boy.
"""

import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory

from apps.customer_management.models import Customer
from apps.notifications.models import (
    NotificationLog,
    NotificationPreferences,
    NotificationTemplate,
)
from apps.setup.models import Configurations
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
    name = factory.Sequence(lambda n: f"customer_{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.name}@test.com")
    phone = "1234567890"

    class Meta:
        model = Customer


class NotificationTemplateFactory(DjangoModelFactory):
    template_name = factory.Sequence(lambda n: f"temp_{n}")
    event_type = factory.Sequence(lambda n: f"event_{n}")
    channel = "email"
    subject = "Subject {{ name }}"
    plain_text = "Plain text {{ name }}"
    html = "HTML {{ name }}"

    class Meta:
        model = NotificationTemplate


class NotificationLogFactory(DjangoModelFactory):
    status = "queued"
    channel = "email"
    context_data = factory.Dict({"name": "Test User"})

    class Meta:
        model = NotificationLog


class NotificationPreferencesFactory(DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    customer = factory.SubFactory(CustomerFactory)
    event_type = "welcome_user"
    preference_type = "email"
    opted_in = True

    class Meta:
        model = NotificationPreferences


class ConfigurationsFactory(DjangoModelFactory):
    interface_type = "notification_configuration"
    details = factory.Dict({"tenant_preferences": ["email"]})

    class Meta:
        model = Configurations
