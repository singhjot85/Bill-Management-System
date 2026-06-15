---
title: Async Tasks & Celery
type: implementation
app: tasks
last_updated: 2025-01-24
tags: [django, celery, tasks, valkey]
---

# Async Tasks & Celery

## Purpose
Enables asynchronous task processing with native support for multi-tenancy.

This app overrides standard Celery behavior to ensure that background tasks are tenant-aware, automatically switching database schemas and maintaining context across worker threads.

## Quick Start
```python
from apps.tasks.registry import TaskNames

# Queuing a task with automatic tenant context
task = TaskNames.PDF_GENERATION.get_task_instance()
task.apply_async_on_commit(task_args=(invoice_id,))
```

## Key Concepts
- **TenantAwareTask**: Overrides standard Celery tasks to automatically inject and extract `_schema_name` from task arguments.
- **Task Registry**: Centralized enum (`TaskNames`) that maps logical names to dotted-path task implementations.
- **On-Commit Queuing**: `apply_async_on_commit` ensures tasks only run after database transactions are finalized.
- **Schema Switching**: `task_prerun` and `task_postrun` signals handle the switching of PostgreSQL search paths before and after task execution.

## Celery Worker Structure
- **Worker**: Processes tasks from Valkey queues.
- **Beat**: Handles scheduled tasks (e.g., recurring bill generation).
- **Concurrency**: Managed via Celery's standard pool settings, with schema switching ensuring isolation within threads.

## Task Registry
All tasks must be registered in `registry.py`:
1. Add module to `TaskLocation`.
2. Define task name and mapping in `TaskNames`.
3. Use `queue_task` or `get_task_instance` for consistent invocation.

## Configuration
- `CELERY_BROKER_URL`: Connection string for Valkey.
- `CELERY_TASK_ALWAYS_EAGER`: Set to `True` during testing for synchronous execution.
- `TASK_RESULT_CHECK_TIMEOUT`: Time to wait for task results when polling.

## Testing
```bash
# Run tasks-specific tests
pytest backend/tests/tasks/
```

## Related Documentation
- [Asynchronous Architecture](../../../docs/architecture/async-system.md)
- [Infrastructure Overview](../../../docs/architecture/overview.md)
