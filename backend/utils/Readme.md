# Backend Utilities

This directory contains reusable utility modules, mixins, and helper classes used across the Django backend to ensure consistency, reduce boilerplate, and enforce architectural standards.

---

## 📂 Directory Structure

| File | Purpose |
| :--- | :--- |
| `admin_utils.py` | Custom Django Admin site configurations and ModelAdmin mixins. |
| `model_utils.py` | Core model mixins (UUID, Soft-Delete, Timestamping, Versioning). |
| `registry_utils.py` | Generic Class Registry pattern for dynamic component resolution. |
| `view_utils.py` | DRF and Django View mixins for authentication and testing. |

---

## 🛠️ Detailed Utility Guide

### 1. Model Utilities (`model_utils.py`)
This is the most critical utility file. It defines the base mixins that almost every model in the system should inherit from.

-   **`BetterModelMixin`**: The standard for most models. Combines UUID primary keys, automatic `created`/`modified` timestamps, and soft-delete capabilities.
-   **`SafeModelMixin`**: Similar to `BetterModelMixin` but uses the default primary key (useful when UUIDs aren't desired).
-   **`SoftDeleteModelMixin`**: Implements custom soft-delete logic, including tracking `deleted_by` and `deleted_at`.
-   **`SimpleVersionModelMixin`**: Provides semver-compatible versioning fields (`major`, `minor`, `patch`) and automatic version string resolution.

**Significance**: Ensures all database records have a consistent audit trail and prevents accidental data loss via soft-deletion.

### 2. Admin Utilities (`admin_utils.py`)
Customizes the Django Admin interface to support multi-tenant isolation and read-only views.

-   **`PublicAdminSite` / `TenantAdminSite`**: Separated admin sites for the Public schema and individual Tenant schemas.
-   **`ReadOnlyAdmin`**: A utility class that disables all "add", "change", and "delete" permissions, making a model read-only in the admin panel (ideal for logs).

**Significance**: Provides a clean separation between platform administration and tenant-level administration.

### 3. Registry Utilities (`registry_utils.py`)
Implements the **Registry Pattern**, which is used throughout the notification and payment systems.

-   **`ClassRegistry`**: A generic class that allows you to register classes against a string key and retrieve them later.

**Significance**: Facilitates the **Strategy Pattern** by allowing the system to dynamically select implementation classes (like different payment gateways or notification channels) at runtime without hardcoded imports.

### 4. View Utilities (`view_utils.py`)
Mixins for Django and DRF views.

-   **`AuthenticatedViewMixin`**: Enforces session and user authentication. It intelligently handles both HTML redirects (for browser users) and JSON 401 responses (for API clients).
-   **`ConnTestMixin`**: A simple ViewSet used to verify connectivity and routing (GET/POST/LIST).

**Significance**: Standardizes authentication checks across non-DRF views and provides debugging tools for developers.

---

## 🚀 Developer Guide

### Using Model Mixins
Always prefer `BetterModelMixin` for new tenant-scoped models.

```python
from utils.model_utils import BetterModelMixin

class MyNewModel(BetterModelMixin):
    name = models.CharField(max_length=100)
```

### Implementing a Registry
Registries are useful for extensible systems.

```python
from utils.registry_utils import ClassRegistry

task_registry = ClassRegistry()

@task_registry.register(key="email_task")
class EmailTask:
    pass

# Retrieve later
task_class = task_registry.get("email_task")
```

### Making an Admin Read-Only
```python
from utils.admin_utils import ReadOnlyAdmin

@admin.register(NotificationLog)
class NotificationLogAdmin(ReadOnlyAdmin):
    pass
```

---

## ⚠️ Operational Guardrails

1.  **Inherit, Don't Re-implement**: Before adding `created_at` or `UUID` fields manually, check if a mixin in `model_utils.py` already provides them.
2.  **Soft-Delete Awareness**: Remember that when using `BetterModelMixin`, "deleting" an object via `.delete()` will only mark `is_removed=True`. To permanently delete, use `hard_delete()` if available or manual SQL.
3.  **Registry Keys**: When using `ClassRegistry`, ensure keys are unique and ideally namespaced (e.g., `app_name.feature_name`).
