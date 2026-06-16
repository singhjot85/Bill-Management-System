from unittest.mock import MagicMock, patch

import pytest
from celery.contrib.django.task import DjangoTask
from celery.result import AsyncResult

from apps.tasks.registry import (
    CeleryTaskExhausted,
    TaskLocation,
    TaskNames,
    TaskQueuingException,
    get_data_from_task_result,
    queue_task,
)


class TestTaskLocation:
    def test_get_autodiscove_tasks(self):
        tasks = TaskLocation.get_autodiscove_tasks()
        assert isinstance(tasks, list)
        assert len(tasks) == len(set(TaskLocation))
        assert "apps.tasks.test_tasks" in tasks
        assert "apps.tasks.invoice_tasks" in tasks


class TestTaskNames:
    def test_task_label(self):
        assert TaskNames.PDF_GENERATION.task_label() == "Generate Pdf"
        assert TaskNames.TEST_TENANT_AWARE_TASK.task_label() == "Test Tenant Awareness"

    def test_task_path(self):
        assert TaskNames.PDF_GENERATION.task_path() == TaskLocation.INVOICE_TASKS.value
        assert TaskNames.TEST_TENANT_AWARE_TASK.task_path() == TaskLocation.TEST_TASKS.value

    def test_celery_name(self):
        expected = f"{TaskLocation.INVOICE_TASKS.value}.generate_pdf"
        assert TaskNames.PDF_GENERATION.celery_name() == expected

    def test_task_id(self):
        idempotency_key = "12345"
        expected = f"{TaskNames.PDF_GENERATION.celery_name()}-{idempotency_key}"
        assert TaskNames.PDF_GENERATION.task_id(idempotency_key) == expected

    def test_get_task_instance(self):
        task = TaskNames.TEST_TENANT_AWARE_TASK.get_task_instance()
        assert isinstance(task, DjangoTask)
        assert task.name == TaskNames.TEST_TENANT_AWARE_TASK.celery_name()

    def test_get_task_instance_import_error(self):
        # Create a dummy TaskNames member with invalid path
        with patch.object(TaskNames.PDF_GENERATION, "task_path", return_value="invalid.path"):
            with pytest.raises(ImportError):
                TaskNames.PDF_GENERATION.get_task_instance()


class TestQueueTask:
    @patch("apps.tasks.registry.TaskNames.get_task_instance")
    def test_queue_task_with_enum(self, mock_get_task):
        mock_task = MagicMock(spec=DjangoTask)
        mock_get_task.return_value = mock_task

        queue_task(TaskNames.TEST_TENANT_AWARE_TASK, on_commit=False)

        mock_task.apply_async.assert_called_once()

    @patch("apps.tasks.registry.TaskNames.get_task_instance")
    def test_queue_task_with_string(self, mock_get_task):
        # This requires the string to be a valid Enum member name
        # TaskNames(task) will be called
        mock_task = MagicMock(spec=DjangoTask)
        mock_get_task.return_value = mock_task

        queue_task("PDF_GENERATION", on_commit=False)

        mock_task.apply_async.assert_called_once()

    def test_queue_task_with_invalid_type(self):
        with pytest.raises(TaskQueuingException):
            queue_task(123)

    @patch("apps.tasks.registry.TaskNames.get_task_instance")
    def test_queue_task_on_commit(self, mock_get_task):
        mock_task = MagicMock(spec=DjangoTask)
        mock_get_task.return_value = mock_task

        result = queue_task(TaskNames.TEST_TENANT_AWARE_TASK, on_commit=True)

        assert result is None
        mock_task.apply_async_on_commit.assert_called_once()

    @patch("apps.tasks.registry.TaskNames.get_task_instance")
    def test__queue_task__task_args_works(self, mock_get_task):
        mock_task = MagicMock(spec=DjangoTask)
        mock_get_task.return_value = mock_task

        _args = ("A", "B", "C")
        _kwargs = {"1": "x", "2": "y", "3": "z"}

        queue_task(TaskNames.TEST_TENANT_AWARE_TASK, on_commit=False, task_args=_args, task_kwargs=_kwargs)

        mock_task.apply_async.assert_called_once_with(args=_args, kwargs=_kwargs)

    def test__queue_task__queue_name_works(self):
        # TODO: Need to implement task_queue's for this
        pass

    @patch("apps.tasks.registry.TaskNames.get_task_instance")
    def test__queue_task__idempotency_key_works(self, mock_get_task):
        mock_task = MagicMock(spec=DjangoTask)
        mock_get_task.return_value = mock_task

        idempotency_key = "1234567"

        queue_task(TaskNames.TEST_TENANT_AWARE_TASK, on_commit=False, idempotency_key=idempotency_key)

        expected = TaskNames.TEST_TENANT_AWARE_TASK.task_id(idempotency_key)
        mock_task.apply_async.assert_called_once_with(args=(), kwargs={}, task_id=expected)

class TestGetDataFromTaskResult:
    @patch("time.sleep", return_value=None)
    def test_get_data_success(self, mock_sleep):
        mock_result = MagicMock(spec=AsyncResult)
        mock_result.ready.return_value = True
        mock_result.get.return_value = {"status": "success"}

        data = get_data_from_task_result(mock_result)

        assert data == {"status": "success"}
        mock_sleep.assert_not_called()

    @patch("time.sleep", return_value=None)
    def test_get_data_exhausted(self, mock_sleep):
        mock_result = MagicMock(spec=AsyncResult)
        mock_result.ready.return_value = False

        with pytest.raises(CeleryTaskExhausted):
            get_data_from_task_result(mock_result)

        # Should have called sleep and ready() several times based on settings
        assert mock_result.ready.call_count > 0
