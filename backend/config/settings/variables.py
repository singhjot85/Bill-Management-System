import os
from pathlib import Path

APP_NAME = "apps"
BASE_DIR = Path(__file__).resolve().parent.parent.parent # Path to /backend
APP_DIR = os.path.join(BASE_DIR, APP_NAME) # Path to /backend/apps

PROJECT_STATIC_PATH = os.path.join(BASE_DIR, "django_templates", "static")
COLLECTED_STATIC_FILES = os.path.join(BASE_DIR, "django_templates", "staticfiles")

TEMPLATES_DIR = os.path.join(BASE_DIR, "django_templates", "templates")

APPLICATION_TIMEZONE = os.getenv("TIME_ZONE", "UTC")

DATABASE_NAME = os.getenv("POSTGRES_DB")
DATABASE_USER = os.getenv("POSTGRES_USER")
DATABASE_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DATABASE_HOST = os.getenv("POSTGRES_HOST")
DATABASE_PORT = os.getenv("POSTGRES_PORT")

SECRET_KEY = os.getenv("DJANGO_SECRETE_KEY", "")
RAZORPAY_API_KEY = os.getenv("RAZORPAY_API_KEY", "")
RAZORPAY_API_SECRETE = os.getenv("RAZORPAY_API_SECRETE", "")
DEFAULT_AUTO_FIELD = os.getenv("DJANGO_DEFAULT_ID", "django.db.models.BigAutoField")

CURRENT_ENV = os.getenv("DJANGO_ENV", "devlopment")

CACHE_PROTCOL = os.getenv("CACHE_PROTCOL", "redis")
CACHE_HOST = os.getenv("CACHE_HOST", "bma_cache")
CACHE_PORT = os.getenv("CACHE_PORT", "6379")
CACHE_DATABASE = os.getenv("CACHE_DATABASE", 0)

BROKER_PROTOCOL = os.getenv("BROKER_PROTOCOL", "redis")
BROKER_HOST = os.getenv("BROKER_HOST", "bma_valkey_broker")
BROKER_PORT = os.getenv("BROKER_PORT", "6378")
BROKER_DATABASE = os.getenv("BROKER_DATABASE", 0)

DEFAULT_TASK_QUEUE_NAME = os.getenv("CELERY_DEFAULT_TASK_QUEUE", "celery_default_queue")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "django-db")
TASK_TIME_LIMIT = os.getenv("CELERY_TASK_TIME_LIMIT", 9 * 60)
TASK_SOFT_TIME_LIMIT = os.getenv("CELERY_TASK_SOFT_TIME_LIMIT", 8 * 60)

# Valkey clustering settings
VALKEY_SOCKET_CONN_TIMEOUT = os.getenv("VALKEY_SOCKET_CONN_TIMEOUT")
VALKEY_SOCKER_TIMEOUT = os.getenv("VALKEY_SOCKER_TIMEOUT")

# DjangoCore email settings
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = os.getenv("EMAIL_PORT", 587)
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", True)
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", False)
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")

EMAIL_FILE_PATH = os.path.join(BASE_DIR, "local_testing", "django-mails")

DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "")
