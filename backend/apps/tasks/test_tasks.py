import logging

from celery import shared_task
from django.db import connection

LOGGER = logging.getLogger(__name__)


@shared_task
def test_tenant_awareness(*args, **kwargs):

    return {"execution_schema": connection.schema_name, "args": args, "kwargs": kwargs}
