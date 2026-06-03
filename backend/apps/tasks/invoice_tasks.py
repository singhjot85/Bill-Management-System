import logging

from celery import shared_task

LOGGER = logging.getLogger()


@shared_task
def test_tenant_awareness(*args, **kwargs):
    from django.db import connection

    LOGGER.debug("Testing connection, current schema >>> %s", connection.schema_name)
    LOGGER.info("Testing connection, current schema >>> %s", connection.schema_name)
    return f"Current Schema >>> {connection.schema_name}"
