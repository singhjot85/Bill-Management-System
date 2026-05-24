import os

from project_apps.tasks.base import TenantAwareCeleryApp
from project_apps.tasks.registry import TaskLocation

# Make sure project settings are setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = TenantAwareCeleryApp()

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(TaskLocation.get_autodiscove_tasks())
