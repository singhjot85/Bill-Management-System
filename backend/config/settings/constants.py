"""
This file list all the apps that are used in the project, this keep the settings.py file clean.
"""

PROJECT_NAME = "bill-management-application"
PROJECT_LABEL = "Bill Management Application"


# ----------------------------
#   Model(s) and their Apps
# ----------------------------

APP_CUSTOMERS = "apps.customer_management"
CUSTOMER_CUSTOMER = "customer_management.Customer"
CUSTOMER_ADDRESS = "customer_management.CustomerAddress"

APP_NOTIFICATIONS = "apps.notifications"
NOTIFICATION_TEMPLATE = "notifications.NotificationTemplate"
NOTIFICATION_LOGS = "notifications.NotificationLog"
NOTIFICATION_PREFERENCES = "notifications.NotificationPreferences"

APP_PAYMENTS = "apps.payments_management"
PAYMENT_INVOICE = "payments_management.Invoice"
PAYMENT_TEMPLATES = "payments_management.Templates"
PAYMENT_PAYMENTS = "payments_management.Payment"

APP_SETUP = "apps.setup"
SETUP_CONFIGURATION = "setup.Configurations"

APP_TENANTS = "apps.tenants"
TENANTS_ORGANIZATION_TENANT = "tenants.OrganizationTenant"
TENANTS_ORGANIZATION_DOMAIN = "tenants.OrganizationDomain"
TENANTS_ORGANIZATION_BRANDING = "tenants.OrganizationBranding"


# ----------------------------
#   Runtime App Classification
# ----------------------------
DEFAULT_DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

SHARED_EXTRA_DEPENDENCIES = [
    "rest_framework",
    "django_tenants",
    "rest_framework.authtoken",
    "dj_rest_auth",
    "constance",
]

PUBLIC_ONLY_EXTRA_DEPENDENCIES = [
    "django_celery_results",
]

PROJECT_APPS = [
    "apps.tenants",
    "apps.setup",
    "apps.customer_management",
    "apps.payments_management",
    "apps.notifications",
]


# -----------------------------
#   Database App Classification
# -----------------------------
DJANGO_TENANT_PUBLIC_APPS = [
    *DEFAULT_DJANGO_APPS,
    *SHARED_EXTRA_DEPENDENCIES,
    *PUBLIC_ONLY_EXTRA_DEPENDENCIES,
    "apps.tenants",
    "apps.setup",
]

DJANGO_TENANT_PRIVATE_APPS = [
    *DEFAULT_DJANGO_APPS,
    *SHARED_EXTRA_DEPENDENCIES,
    "apps.customer_management",
    "apps.payments_management",
    "apps.setup",
    "apps.notifications",
]


# -----------------------------
#   dj-rest-auth Constants
# -----------------------------
USER_DETAIL_SERIALIZER = "apps.tenants.serializers.UserSerializer"


# -----------------------------
#   Redis Constants
# -----------------------------
DJANGO_REDIS_IGNORE_EXCEPTIONS = True
REDIS_DEFAULT_BACKEND = "django_redis.cache.RedisCache"
REDIS_CLUSTER_DEFAULT_OPTIONS = {
    "CLIENT_CLASS": "django_redis.client.DefaultClient",
    "PICKLED_VERSION": 5,
}
REDIS_DEFAULT_OPTIONS = {
    "CLIENT_CLASS": "django_redis.client.DefaultClient",
}


# -----------------------------
#   Valkey Constants
# -----------------------------
VALKEY_DEFAULT_BACKEND = "django_valkey.cluster_cache.cache.ClusterValkeyCache"
VALKEY_CLUSTER_DEFAULT_OPTIONS = {
    "CLIENT_CLASS": "config.valkey_cluster_client.PatchedClusterClient",
    "CONNECTION_POOL_KWARGS": {
        "socket_connection_timeout": 5,
        "socket_timeout": 5,
    },
}
VALKEY_DEFAULT_OPTIONS = {
    "CLIENT_CLASS": "django_valkey.client.DefaultClient",
}


# -----------------------------
#   django-constance Constants
# -----------------------------
    
RADIO_BUTTON_CONSTANCE: tuple[str, list[str, dict]] = (
    "yes_no_null_select",
    [
        "django.forms.fields.ChoiceField",
        {"widget": "django.forms.Select", "choices": ((None, "----"), (True, "Activate"), (False, "Deactivate"))},
    ],
)


# -----------------------------
#   Custom Constants
# -----------------------------
TASK_RESULT_CHECK_RETRIES = 10
TASK_RESULT_CHECK_TIMEOUT = 10  # Seconds

LOCAL_ENVS = ["local", "dev", "devlopment"]
