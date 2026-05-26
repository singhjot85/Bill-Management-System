import os
from pathlib import Path

APP_NAME = "project_apps"
BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = os.path.join(BASE_DIR, APP_NAME)

PROJECT_STATIC_PATH = os.path.join(BASE_DIR, "project_templating", "static")

TEMPLATES_DIR = os.path.join(BASE_DIR, "project_templating", "templates")

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

CACHE_PROVIDER = os.getenv("CACHE_PROVIDER", "valkey")
CACHE_HOST = os.getenv("CACHE_HOST", "bma_cache")
CACHE_PORT = os.getenv("CACHE_PORT", "6379")

BROKER_PROVIDER = os.getenv("BROKER_PROVIDER", "redis")
BROKER_HOST = os.getenv("BROKER_HOST", "bma_valkey_broker")
BROKER_PORT = os.getenv("BROKER_PORT", "6378")

DEFAULT_TASK_QUEUE_NAME = os.getenv("CELERY_DEFAULT_TASK_QUEUE", "celery_default_queue")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "django-db")
TASK_TIME_LIMIT = os.getenv("CELERY_TASK_TIME_LIMIT", 9 * 60)
TASK_SOFT_TIME_LIMIT = os.getenv("CELERY_TASK_SOFT_TIME_LIMIT", 8 * 60)

# Valkey clustering settings
VALKEY_SOCKET_CONN_TIMEOUT = os.getenv("VALKEY_SOCKET_CONN_TIMEOUT")
VALKEY_SOCKER_TIMEOUT = os.getenv("VALKEY_SOCKER_TIMEOUT")
