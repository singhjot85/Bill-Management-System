"""
This file list all the apps that are used in the project, this keep the settings.py file clean.
"""

TENANT_APP_NAME = "tenants"
TENANT_MODEL_NAME = "OrganizationTenant"
DOMAIN_MODEL_NAME = "OrganizationDomain"

DEFAULT_DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

EXTRA_DEPENDENCIES = [
    "rest_framework",
    "django_tenants",
    "rest_framework.authtoken",
    "dj_rest_auth",
]

PROJECT_APPS = [
    "project_apps.tenants",
    "project_apps.setup",
    "project_apps.customer_management",
    "project_apps.payments_management",
]

DJANGO_TENANT_PUBLIC_APPS = [*DEFAULT_DJANGO_APPS, *EXTRA_DEPENDENCIES, "project_apps.tenants", "project_apps.setup"]

DJANGO_TENANT_PRIVATE_APPS = [
    *DEFAULT_DJANGO_APPS,
    *EXTRA_DEPENDENCIES,
    "project_apps.customer_management",
    "project_apps.payments_management",
    "project_apps.setup",
]

CUSTOMER_CUSTOMER = "customer_management.Customer"
CUSTOMER_ADDRESS = "customer_management.CustomerAddress"
PAYMENT_INVOICE = "payments_management.Invoice"
PAYMENT_TEMPLATES = "payments_management.Templates"

LOCAL_ENVS = ["local", "dev", "development"]

USER_DETAIL_SERIALIZER = "project_apps.tenants.serializers.UserSerializer"