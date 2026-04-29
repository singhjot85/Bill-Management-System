"""
Infra specific varibles will stay in this files
Variables required to construct them or extra varibles used by project will be imported.
This is done so that project settings do not bloat over.
"""

import os

from .apps import *
from .variables import *


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

SECRET_KEY = os.getenv("DJANGO_SECRETE_KEY", "")
RAZORPAY_API_KEY = os.getenv("RAZORPAY_API_SECRETE", "")
RAZORPAY_API_SECRETE = os.getenv("RAZORPAY_API_SECRETE", "")
DEFAULT_AUTO_FIELD = os.getenv("DJANGO_DEFAULT_ID", "django.db.models.BigAutoField")

USE_TZ = True
USE_I18N = True
TIME_ZONE = "UTC"
LANGUAGE_CODE = "en-us"

BOOTSRAP_SCHEMA_NAME = "localclient"

CURRENT_ENV = os.getenv("DJANGO_ENV", "devlopment")
LOCAL_ENVS = ["local", "dev", "devlopment"]

if CURRENT_ENV in LOCAL_ENVS:
    DEBUG = True
    ALLOWED_HOSTS = []
    WSGI_APPLICATION = "config.wsgi.application"
else:
    # TODO: Write WSGI and  ALLOWED_HOSTS configuration for production
    DEBUG = False
    ALLOWED_HOSTS = []
    WSGI_APPLICATION = ""

    # Kept here, so we don't foget to build this logic
    def get_resolved_domains():
        pass

    RESOLVED_DOMAINS = get_resolved_domains()
