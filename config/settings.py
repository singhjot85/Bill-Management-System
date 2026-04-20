import os
from pathlib import Path

APP_NAME = "bma"
BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = os.path.join(BASE_DIR, APP_NAME)

SECRET_KEY = os.getenv("DJANGO_SECRETE_KEY", "")
RAZORPAY_API_KEY = os.getenv("RAZORPAY_API_SECRETE", "")
RAZORPAY_API_SECRETE = os.getenv("RAZORPAY_API_SECRETE", "")
DEFAULT_AUTO_FIELD = os.getenv("DJANGO_DEFAULT_ID", "django.db.models.BigAutoField")


LOCAL_ENVS = ["local", "dev", "devlopment"]
if os.getenv("DJANGO_ENV", "devlopment") in LOCAL_ENVS:
    DEBUG = True
    ALLOWED_HOSTS = []
    WSGI_APPLICATION = "config.wsgi.application"
else:
    # TODO: Write WSGI and  ALLOWED_HOSTS configuration for production
    DEBUG = False
    ALLOWED_HOSTS = []
    WSGI_APPLICATION = ""


USE_TZ = True
USE_I18N = True
TIME_ZONE = "UTC"
LANGUAGE_CODE = "en-us"

STATIC_URL = "static/"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR / "static"),
]


ROOT_URLCONF = "config.routers"

AUTH_USER_MODEL = "core.BaseUserModel"
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "rest_framework",
    "bma.requests",
    "bma.payments",
    "bma.core",
]


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_TEMPLATE_DIR = os.path.join(BASE_DIR, "bma", "core", "templates")
PAYMENTS_TEMPLATE_DIR = os.path.join(BASE_DIR, "bma", "payments", "templates")
REQUESTS_TEMPLATE_DIR = os.path.join(BASE_DIR, "bma", "requests", "templates")
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [AUTH_TEMPLATE_DIR, PAYMENTS_TEMPLATE_DIR, REQUESTS_TEMPLATE_DIR],
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
