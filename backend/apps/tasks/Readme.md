# Tasks App

This is not a Django registered app. Instead, this app will be consumed by celery to generate asynchronous tasks.
As we are using django-tenants to isolate tenant databases, the celery module doesn't have a direct support for that, so we are using some custom defined logic to make the tasks tenant aware.

## Directory Structure
```
tasks\
    |- base.py         # Configuration and Celery Overrides
    |- registry.py     # Constants and Utils for celery tasks
    |- invoice_tasks.py # Invoice related tasks
    |- test_tasks.py    # Test/Utility tasks
```

- **base.py**: Configuration and Celery Overrides. Defines the `TenantAwareCeleryApp` and `TenantAwareTask` to ensure tenant context is maintained.
- **registry.py**: Constants and Utils for celery tasks. Provides a central registry for task names, locations, and a standardized `queue_task` wrapper.


## TenantAwareCeleryApp
*Path*: `backend/apps/tasks/base.py::TenantAwareCeleryApp`

Overrides the `celery.app.Celery` class to register the celery application with custom `TenantAwareTask` class. This is the entry point for the Celery application in the project.

## TenantAwareTask
*Path*: `backend/apps/tasks/base.py::TenantAwareTask`

Uses `celery.contrib.django.task.DjangoTask` as base, and overrides `apply_async`, `apply`, to add current schema name, so that user doesn't have to manually add schema_name every time they queue a task.

So a common user use case would look like:

- `asyn_task.apply_async(...)`, and this will automatically have schema name under `_schema_name` kwargs.

### Why `celery.contrib.django.task.DjangoTask`?
Because we are using a django application, tasks are often queued within database transactions. If a task starts before the transaction is committed, it won't see the database changes.

- `DjangoTask` has an `apply_async_on_commit` method which queues the task only after the database transaction is successfully committed.

**Example:**
```python
from apps.tasks.registry import TaskNames

def generate_invoice(invoice_id):
    # Within a view or service
    task = TaskNames.PDF_GENERATION.get_task_instance()

    # Automatically includes _schema_name and waits for DB commit
    task.apply_async_on_commit(task_args=(invoice_id,))
```

# Signals

Signals are essentially a way for decoupled parts of an application to communicate with each other. They are a direct implementation of the Observer Design Pattern (often referred to as Publish-Subscribe).

## task_prerun
*Path*: `backend/apps/tasks/base.py::switch_schema_context`

Added a `switch_schema_context` to `celery.signals.task_prerun` signal.

**Usecase**: Before a task starts, it extracts `_schema_name` from the task's keyword arguments. It then uses `django-tenants` to switch the database connection to that specific tenant's schema. This ensures that any ORM calls within the task target the correct tenant database.

## task_postrun
*Path*: `backend/apps/tasks/base.py::restore_schema_context`

Added a `restore_schema_context` to `celery.signals.task_postrun` signal.

**Usecase**: After a task completes (successfully or not), it restores the database connection to the schema it was using before the task started. This is crucial for preventing schema "leakage" between different task executions on the same Celery worker thread.

## TaskLocation
*Path*: `backend/apps/tasks/registry.py::TaskLocation`
Register all your celery task modules here. This Enum is used by `autodiscover_tasks` during Celery initialization and for importing tasks dynamically.

**Usecase**: When adding a new file like `apps/tasks/report_tasks.py`, add a member `REPORTS = "apps.tasks.report_tasks"` to this Enum.

## TaskNames
*Path*: `backend/apps/tasks/registry.py::TaskNames`
Centralized registry for all task definitions. It maps a logical name to the function name and its location.

**Features**:
- `task_label()`: Returns a human-readable name.
- `celery_name()`: Returns the full dotted path (e.g., `apps.tasks.invoice_tasks.generate_pdf`).
- `task_id(idempotency_key)`: Generates a unique task ID to ensure idempotency.
- `get_task_instance()`: Dynamically imports the task function.

## FailureModes
*Path*: `backend/apps/tasks/registry.py::FailureModes`

Failure Mode constants:
- `SILENT`: Log but don't re-raise.
- `ALERT`: Trigger alerts/notifications.
- `DLQ`: Move to Dead Letter Queue (future implementation).

## queue_task
A wrapper over celery's `task.delay`/`task.apply_async` to standardize task queuing.

**Benefits**:
- Standardizes how tasks are called across the codebase.
- Handles `on_commit` logic automatically.
- Validates task references (can pass string name, `TaskNames` member, or task instance).

## get_data_from_task_result
Helper to fetch data from `AsyncResult` instance provided by celery task.

**Usecase**: Used when you need to wait for a task result in a synchronous manner (e.g., in a test or a specific CLI command). It polls the result based on `TASK_RESULT_CHECK_RETRIES` and `TASK_RESULT_CHECK_TIMEOUT` settings.

**Note**: Avoid using this in web views as it blocks the worker/thread.
