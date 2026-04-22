import os
from pathlib import Path

APP_NAME = "project_apps"
BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = os.path.join(BASE_DIR, APP_NAME)

STATICFILES_DIRS = [
    os.path.join(BASE_DIR / "static"),
]

TENANT_APP_NAME = "tenants"
TENANT_MODEL_NAME = "OrganizationTenant"
DOMAIN_MODEL_NAME = "OrganizatinDomain"

AUTH_TEMPLATE_DIR = os.path.join(APP_DIR, "bma2", "core", "templates")
PAYMENTS_TEMPLATE_DIR = os.path.join(APP_DIR, "bma2", "payments", "templates")
REQUESTS_TEMPLATE_DIR = os.path.join(APP_DIR, "bma2", "requests", "templates")

DATABASE_NAME = os.environ.get("DB_NAME")
DATABASE_USER = os.environ.get("DB_USER")
DATABASE_PASSWORD = os.environ.get("DB_PASS")
DATABASE_HOST = os.environ.get("DB_HOST")
DATABASE_PORT = os.environ.get("DB_PORT")