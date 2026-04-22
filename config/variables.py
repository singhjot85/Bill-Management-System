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

DATABASE_NAME = os.getenv("POSTGRES_DB")
DATABASE_USER = os.getenv("POSTGRES_USER")
DATABASE_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DATABASE_HOST = os.getenv("POSTGRES_HOST")
DATABASE_PORT = os.getenv("POSTGRES_PORT")