import os

from backend.apps.tasks import TaskLocation, TenantAwareCeleryApp

# Make sure project settings are setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.config.settings.base")

from django.conf import settings  # noqa E402

PROJECT_NAME = settings.PROJECT_NAME

app = TenantAwareCeleryApp(PROJECT_NAME)

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(TaskLocation.get_autodiscove_tasks())
