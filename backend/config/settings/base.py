"""
Infra specific varibles will stay in this files
.constants : Settings Constant even at runtime
.variables : Settings that may vary at runtime
.resolvers : Keeps this file clean and perevent circular imports.
"""

from config.settings.constants import *
from config.settings.resolvers import (
    get_broker_url,
    get_cache_url,
    get_resolved_cache_options,
    set_default_email_from,
)
from config.settings.variables import *

STATICFILES_DIRS = [PROJECT_STATIC_PATH]
STATIC_URL = "static/"

ROOT_URLCONF = "config.routers"
PUBLIC_SCHEMA_URLCONF = "config.public_routers"

TENANT_MODEL = f"{TENANT_APP_NAME}.{TENANT_MODEL_NAME}"
TENANT_DOMAIN_MODEL = f"{TENANT_APP_NAME}.{DOMAIN_MODEL_NAME}"

INSTALLED_APPS = [
    *DEFAULT_DJANGO_APPS,
    *SHARED_EXTRA_DEPENDENCIES,
    *PUBLIC_ONLY_EXTRA_DEPENDENCIES,
    *PROJECT_APPS,
]

SHARED_APPS = DJANGO_TENANT_PUBLIC_APPS
TENANT_APPS = DJANGO_TENANT_PRIVATE_APPS
TENANT_SYNC_ROUTER = "django_tenants.routers.TenantSyncRouter"

DATABASE_ROUTERS = [
    # This is what figure's out what will go in INSTALLED_APPS, when running
    TENANT_SYNC_ROUTER
]

DATABASES = {
    "default": {
        "ENGINE": "django_tenants.postgresql_backend",
        "NAME": DATABASE_NAME,
        "USER": DATABASE_USER,
        "PASSWORD": DATABASE_PASSWORD,
        "HOST": DATABASE_HOST,
        "PORT": DATABASE_PORT,
    }
}

CACHE_URL = get_cache_url()
CACHE_BACKEND, RESOLVED_CACHE_OPTIONS = get_resolved_cache_options()
CACHES = {
    "default": {
        "BACKEND": CACHE_BACKEND,
        "LOCATION": CACHE_URL,
        "OPTIONS": RESOLVED_CACHE_OPTIONS,
        "IGNORE_EXCEPTIONS": True,
        "TIMEOUT": 3600,
    },
}

# https://docs.celeryq.dev/en/latest/userguide/configuration.html#
CELERY_BROKER_URL = get_broker_url()
CELERY_RESULT_BACKEND = RESULT_BACKEND

CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

CELERY_TIMEZONE = APPLICATION_TIMEZONE

CELERY_TASK_ALWAYS_EAGER = False  # Eager task run on same caller process
CELERY_TASK_TRACK_STARTED = True  # Save's `Started` as one of the task status.
CELERY_TASK_TIME_LIMIT = TASK_TIME_LIMIT
CELERY_TASK_SOFT_TIME_LIMIT = TASK_SOFT_TIME_LIMIT

# Writes extended results to backend (name, args, kwargs, worker, retries, queue, delivery_info).
CELERY_RESULT_EXTENDED = True
CELERY_DEFAULT_TASK_QUEUE = DEFAULT_TASK_QUEUE_NAME

# Need to define this explicilty fo celery
TENANT_DB_ALIAS = "default"

# CELERY_TASK_ROUTES = {
#     "task_name": {"queue": "queue_name"}
# }

# CELERY_BEAT_SCHEDULER = "config.beat.CustomDatabaseScheduler"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMPLATES_DIR],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


MIDDLEWARE = [
    "django_tenants.middleware.main.TenantMainMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

REST_AUTH = {"USER_DETAILS_SERIALIZER": USER_DETAIL_SERIALIZER}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# ------------------
#  django-constance
# ------------------

CONSTANCE_ADDITIONAL_FIELDS = {RADIO_BUTTON_CONSTANCE[0]: RADIO_BUTTON_CONSTANCE[1]}

CONSTANCE_CONFIG = {
    # "KEY": ("default_value", "description")
    "USE_MOCK_INTEGRATIONS": (True, "Use Mock Integrtion or Real One's")
}

CONSTANCE_CONFIG_FIELDSETS = {
    "Integrations": {
        "fields": ("USE_MOCK_INTEGRATIONS",),
        "collapse": False
    }
}


USE_TZ = True
TIME_ZONE = APPLICATION_TIMEZONE

USE_I18N = True
LANGUAGE_CODE = "en-us"

set_default_email_from()

if CURRENT_ENV in LOCAL_ENVS:
    DEBUG = True
    ALLOWED_HOSTS = []
    WSGI_APPLICATION = "config.wsgi.application"
else:
    # TODO: Write WSGI and  ALLOWED_HOSTS configuration for production
    DEBUG = False
    ALLOWED_HOSTS = []
    WSGI_APPLICATION = ""
