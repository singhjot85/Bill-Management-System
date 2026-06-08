from typing import TYPE_CHECKING

from django.db import connection
from django.conf import settings
from django_tenants.utils import get_public_schema_name, schema_context

from apps.tasks.registry import TaskNames, queue_task, get_data_from_task_result

if TYPE_CHECKING:
    from celery.result import AsyncResult
    from apps.tasks.base import TenantAwareTask

TENANT_SCHEMA_NAME = settings.TENANT_SCHEMA_NAME
PUBLIC_SCHEMA_NAME = get_public_schema_name()


class TestTenantAwareTask:
    """
    Tests for TestTenantAwareTask, to test if schema switching works as expected.
    NOTE:
        Our test suite execute tests in tenant schema rather than public schema.
        So we'll test two cases:
            Queued in (public Schema) -> Executes in public only
            Queued in (private Schema) -> Executes in private only
    """

    def setup_method(self):
        self.task_name = TaskNames.TEST_TENANT_AWARE_TASK
        self.task: TenantAwareTask = self.task_name.get_task_instance()

    def test__add_current_schema__appends_schema_name(self):
        """Checks if the task adds schema_name to task kwargs"""
        kwargs = {}
        self.task._add_current_schema(kwargs)
        assert "_schema_name" in kwargs
        assert kwargs["_schema_name"] == connection.schema_name

    def test__task_queued_from_private_schema__executes_in_private(self):
        """Task queued under private schema should execute in private schema only"""

        assert (
            connection.schema_name == TENANT_SCHEMA_NAME
        ), "Test not in correct schema, ideally this test should run in private schema"

        task_result: "AsyncResult" = queue_task(self.task, on_commit=False)
        data = get_data_from_task_result(task_result)
        assert data["execution_schema"] == TENANT_SCHEMA_NAME

    def test__task_queued_from_public_schema__executes_in_public(self, public_db):
        """Task queued under public schema should execute in public schema only"""

        assert (
            connection.schema_name == PUBLIC_SCHEMA_NAME
        ), "Test should start in the public schema context"

        task_result: "AsyncResult" = queue_task(self.task, on_commit=False)
        data = get_data_from_task_result(task_result)
        assert data["execution_schema"] == PUBLIC_SCHEMA_NAME

    def test__after_task_queuing_schema_is_restored(self):
        from django_tenants.utils import schema_context

        with schema_context(PUBLIC_SCHEMA_NAME):
            task_result: "AsyncResult" = queue_task(self.task, on_commit=False)
            data = get_data_from_task_result(task_result)
            assert data["execution_schema"] == PUBLIC_SCHEMA_NAME
        
        assert connection.schema_name == TENANT_SCHEMA_NAME