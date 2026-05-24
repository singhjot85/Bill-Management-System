from enum import Enum


class TaskLocation(Enum):
    """Task file path for auto discover_tasks, whenever a new task file is created register it here"""

    INVOICE_TASK = "project_apps.tasks.invoice_tasks"

    @staticmethod
    def get_autodiscove_tasks():
        """Getter for autodiscover, handle's duplicate registractions also"""
        taskfile_path = {t.value for t in TaskLocation}
        return list(taskfile_path)


class TaskNames(Enum):

    # PDF_GENERATION = 'bma.invoice.generate_pdf'
    PDF_GENERATION = "generate_pdf", TaskLocation.INVOICE_TASK.value

    def task_label(self):
        return self.value[0].replace("_", " ").title().strip()

    def task_path(self):
        return self.value[1]

    def celery_name(self) -> str:
        """Simple Getter that resolves task names to be registered in celery"""
        task_exact_name = self.value[0]
        task_location = self.value[1]

        return f"{task_location}-{task_exact_name}"

    def task_id(self, idempotency_key: str) -> str:
        """For idempotency in task queuing use this attribute while queuing task."""
        return f"{self.celery_name()}-{idempotency_key}"


class FailureModes(Enum):

    SILENT = "silent"
    ALERT = "alert"
    DLQ = "dlq"
