"""
Infra specific varibles will stay in this files
.constants : Settings Constant even at runtime
.variables : Settings that may vary at runtime
"""

# TODO: Explicitly define each import to make debugging easier
from .constants import *
from .variables import *
from .setting_resolvers import get_resolved_cache_options, get_cache_url

STATICFILES_DIRS = [PROJECT_STATIC_PATH]
STATIC_URL = "static/"

ROOT_URLCONF = "config.routers"
PUBLIC_SCHEMA_URLCONF = "config.public_routers"

TENANT_MODEL = f"{TENANT_APP_NAME}.{TENANT_MODEL_NAME}"
TENANT_DOMAIN_MODEL = f"{TENANT_APP_NAME}.{DOMAIN_MODEL_NAME}"

INSTALLED_APPS = [
    *DEFAULT_DJANGO_APPS,
    *EXTRA_DEPENDENCIES,
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

USE_TZ = True
USE_I18N = True
TIME_ZONE = "UTC"
LANGUAGE_CODE = "en-us"

if CURRENT_ENV in LOCAL_ENVS:
    DEBUG = True
    ALLOWED_HOSTS = []
    WSGI_APPLICATION = "config.wsgi.application"
else:
    # TODO: Write WSGI and  ALLOWED_HOSTS configuration for production
    DEBUG = False
    ALLOWED_HOSTS = []
    WSGI_APPLICATION = ""
