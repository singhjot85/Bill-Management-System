from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

from celery.result import AsyncResult
from django.conf import settings
from django.db import connection
from django_tenants.utils import get_public_schema_name

from apps.tasks.registry import TaskNames, queue_task

if TYPE_CHECKING:
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

    @patch("celery.contrib.django.task.DjangoTask.apply_async")
    def test__task_queued_from_private_schema__executes_in_private(self, mock_apply_async):
        """Task queued under private schema should inject private schema only"""
        fake_result = MagicMock(spec=AsyncResult)
        mock_apply_async.return_value = fake_result

        assert (
            connection.schema_name == TENANT_SCHEMA_NAME
        ), "Test not in correct schema, ideally this test should run in private schema"

        result = queue_task(self.task, on_commit=False)

        assert result is fake_result
        mock_apply_async.assert_called_once()
        called_args, _ = mock_apply_async.call_args
        assert called_args[1]["_schema_name"] == TENANT_SCHEMA_NAME

    @patch("celery.contrib.django.task.DjangoTask.apply_async")
    def test__task_queued_from_public_schema__executes_in_public(self, mock_apply_async, public_db):
        """Task queued under public schema should inject public schema only"""
        fake_result = MagicMock(spec=AsyncResult)
        mock_apply_async.return_value = fake_result

        assert connection.schema_name == PUBLIC_SCHEMA_NAME, "Test should start in the public schema context"

        result = queue_task(self.task, on_commit=False)

        assert result is fake_result
        mock_apply_async.assert_called_once()
        called_args, _ = mock_apply_async.call_args
        assert called_args[1]["_schema_name"] == PUBLIC_SCHEMA_NAME

    @patch("celery.contrib.django.task.DjangoTask.apply_async")
    def test__after_task_queuing_schema_is_restored(self, mock_apply_async):
        from django_tenants.utils import schema_context

        fake_result = MagicMock(spec=AsyncResult)
        mock_apply_async.return_value = fake_result

        with schema_context(PUBLIC_SCHEMA_NAME):
            result = queue_task(self.task, on_commit=False)
            assert result is fake_result
            mock_apply_async.assert_called_once()
            called_args, _ = mock_apply_async.call_args
            assert called_args[1]["_schema_name"] == PUBLIC_SCHEMA_NAME

        assert connection.schema_name == TENANT_SCHEMA_NAME
