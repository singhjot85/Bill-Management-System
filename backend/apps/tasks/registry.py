"""
This registry file serves as both a constant and a util file.
It handles all kinds of constants and utilities related to async tasks
"""

from enum import Enum
from importlib import import_module
from typing import TYPE_CHECKING, Optional, TypeAlias, Union

if TYPE_CHECKING:
    from celery.contrib.django.task import DjangoTask
    from celery.result import AsyncResult

TaskReference: TypeAlias = Union[str, "TaskNames", "DjangoTask"]


class TaskLocation(Enum):
    """Task file path for auto discover_tasks, whenever a new task file is created register it here"""

    INVOICE_TASK = "apps.tasks.invoice_tasks"

    @staticmethod
    def get_autodiscove_tasks():
        """Getter for autodiscover, handle's duplicate registractions also"""
        taskfile_path = {t.value for t in TaskLocation}
        return list(taskfile_path)


class TaskNames(Enum):

    PDF_GENERATION = "generate_pdf", TaskLocation.INVOICE_TASK.value

    def task_label(self) -> str:
        """Returns a user friendly task label for current"""
        return self.value[0].replace("_", " ").title().strip()

    def task_path(self):
        """Returns dotted path to task"""
        return self.value[1]

    def celery_name(self) -> str:
        """Simple Getter that resolves task names to be registered in celery"""
        task_exact_name = self.value[0]
        task_location = self.value[1]

        return f"{task_location}-{task_exact_name}"

    def task_id(self, idempotency_key: str) -> str:
        """For idempotency in task queuing use this attribute while queuing task."""
        return f"{self.celery_name()}-{idempotency_key}"

    def get_task_instance(self) -> "DjangoTask":
        try:
            return import_module(self.task_path()).__getattribute__(self.value[0])
        except ImportError:
            raise ImportError("Error importing task")


class FailureModes(Enum):

    SILENT = "silent"
    ALERT = "alert"
    DLQ = "dlq"


class TaskQueuingException:
    pass


def queue_task(
    task: TaskReference,
    on_commit: bool = True,
    task_args=None,
    task_kwargs=None,
    *args,
    **kwargs,
) -> Optional["AsyncResult"]:
    """
    A wrapper over celery's `task.delay`/`task.apply_async` to standardize task queuing.
    This wrapper make's it easier to modify task queuing behaviour
    args:
        on_commit (bool): Whether to queue task after current db-transaction commit or not.
            defaults to True.
        task_args (tuple, optional): Set of argument's to be passed to the task directly.
            Defaults to None.
        task_kwargs (dict, optional): Set of keyword arguments to be passed to the task directly.
            Defaults to None.
    kwargs:
        queue_name (str, optional): Task queue name, in which the task is to be pushed.
            default's to None
        task_id (str): Task Id, to ensure idempotency (i.e. one task run's only once even if queued multiple times).
            default's to None
    Returns:
        (AsyncResult, None): Instance of celery's AsyncResult
            NOTE: Before using AsyncResult always check if result is available i.e. `AsyncResult.ready()`
    """
    task_args = task_args or tuple()
    task_kwargs = task_kwargs or {}

    if isinstance(task, str):
        task = TaskNames(task).get_task_instance()
    elif isinstance(task, TaskNames):
        task = task.get_task_instance()

    if not isinstance(task, DjangoTask):
        raise TaskQueuingException("Invalid argument type for task!")

    task: DjangoTask
    if on_commit:
        task.apply_async_on_commit(args=task_args, kwargs=task_kwargs, *args, **kwargs)
    else:
        return task.apply_async(args=task_args, kwargs=task_kwargs, *args, **kwargs)

    return None
