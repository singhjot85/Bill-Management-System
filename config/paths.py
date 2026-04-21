import os
from pathlib import Path

APP_NAME = "project_apps"
BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = os.path.join(BASE_DIR, APP_NAME)

STATICFILES_DIRS = [
    os.path.join(BASE_DIR / "static"),
]

AUTH_TEMPLATE_DIR = os.path.join(APP_DIR, "bma2", "core", "templates")
PAYMENTS_TEMPLATE_DIR = os.path.join(APP_DIR, "bma2", "payments", "templates")
REQUESTS_TEMPLATE_DIR = os.path.join(APP_DIR, "bma2", "requests", "templates")
