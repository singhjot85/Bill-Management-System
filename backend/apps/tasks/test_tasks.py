import logging

from django.db import connection
from celery import shared_task

LOGGER = logging.getLogger()

@shared_task
def test_tenant_awareness(*args, **kwargs):    

    return {"execution_schema": connection.schema_name}