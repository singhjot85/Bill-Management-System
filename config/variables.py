import os
from pathlib import Path

APP_NAME = "project_apps"
BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = os.path.join(BASE_DIR, APP_NAME)

PROJECT_STATIC_PATH = os.path.join(BASE_DIR, "project_templating", "static")

TEMPLATES_DIR = os.path.join(BASE_DIR, "project_templating", "templates")

DATABASE_NAME = os.getenv("POSTGRES_DB")
DATABASE_USER = os.getenv("POSTGRES_USER")
DATABASE_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DATABASE_HOST = os.getenv("POSTGRES_HOST")
DATABASE_PORT = os.getenv("POSTGRES_PORT")

SECRET_KEY = os.getenv("DJANGO_SECRETE_KEY", "")
RAZORPAY_API_KEY = os.getenv("RAZORPAY_API_KEY", "")
RAZORPAY_API_SECRETE = os.getenv("RAZORPAY_API_SECRETE", "")
DEFAULT_AUTO_FIELD = os.getenv("DJANGO_DEFAULT_ID", "django.db.models.BigAutoField")

BOOTSRAP_SCHEMA_NAME = os.getenv("BOOTSTRAP_SCHEMA", "localclient")
DEV_PASS = os.getenv("DEV_PASS")
PUBLIC_USERNAME = os.getenv("PUBLIC_USERNAME")
PUBLIC_PASSWORD = os.getenv("PUBLIC_PASSWORD")

CURRENT_ENV = os.getenv("DJANGO_ENV", "devlopment")
