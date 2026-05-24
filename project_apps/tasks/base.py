"""
This file contain the celery app used in project, the app is overriden to provide tenant context to celery tasks.
NOTE: Never do a dependecy import in this file, or any import that might trigger django settings,
    Make sure you do lazy imports only, if needed do after setting's import
"""

import copy
import logging
import os

from celery import Celery, Task
from django.db import connection

from project_apps.tasks.registry import FailureModes

# Make sure project settings are setup before any import that might look for django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
from django_tenants.utils import schema_context  # noqa: E402

LOGGER = logging.getLogger()


class TenantAwareTask(Task):
    abstract = True
    failure_mode = FailureModes.SILENT.value

    def apply_async(
        self, args=None, kwargs=None, task_id=None, producer=None, link=None, link_error=None, shadow=None, **options
    ):
        kwargs = kwargs or {}

        if "_schema_name" not in kwargs:
            kwargs["_schema_name"] == connection.schema_name
        return super().apply_async(args, kwargs, task_id, producer, link, link_error, shadow, **options)

    def __call__(self, *args, **kwargs):
        schema_name = kwargs.pop("_schema_name")
        with schema_context(schema_name):
            return super().__call__(*args, **kwargs)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        if self.failure_mode == FailureModes.DLQ.value:
            self._handle_dead_letter_queues(exc, task_id, args, kwargs)
        elif self.failure_mode == FailureModes.ALERT.value:
            self._handle_alerts(exc, task_id)
        else:
            self._handle_silent_failure(exc)

        return super().on_failure(exc, task_id, args, kwargs, einfo)

    # TODO: Implement these handlers
    def _handle_dead_letter_queues(self, exc, task_id, args, kwargs):
        pass

    def _handle_silent_failure(self, exc):
        LOGGER.error("Error in async task", exc_info=exc)

    def _handle_alerts(self, exc):
        pass


def add_schema_name_to_headers(headers: dict = None):
    if headers and "_schema_name" in headers:
        return headers

    headers = copy.deepcopy(headers) if headers else {}
    headers["_schema_name"] = connection.schema_name
    return headers


class TenantAwareCeleryApp(Celery):
    """
    Overriden to add schema_name to send_task, i.e. each task has a schema_name as first parameter.
    Also uses TenantAwareTask that does schema_context switching before executing the task
    """

    task_cls = "project_apps.tasks.base.TenantAwareTask"

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("task_cls", self.task_cls)
        super().__init__(*args, **kwargs)

    def create_task_cls(self):
        return self.subclass_with_self(self.task_cls, abstract=True, name="TenantAwareTask", attribute="_app")

    def send_task(self, name, args=None, kwargs=None, *arg, **options):
        return super().send_task(name, args, kwargs, *arg, **options)
