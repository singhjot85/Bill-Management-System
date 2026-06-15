---
title: Backend Utilities
type: implementation
app: utils
last_updated: 2025-01-24
tags: [django, utilities, mixins]
---

# Backend Utilities

## Purpose
Reusable utility modules, mixins, and helper classes to ensure consistency and reduce boilerplate.

These utilities enforce architectural standards across models, views, and admin interfaces, providing common patterns like soft-deletion, UUID primary keys, and dynamic class registration.

## Quick Start
```python
from utils.model_utils import BetterModelMixin

class MyNewModel(BetterModelMixin):
    # Inherits UUID PK, created/modified timestamps, and soft-delete
    name = models.CharField(max_length=100)
```

## Key Concepts
- **Core Mixins**: Standardized base classes for models (`BetterModelMixin`, `SafeModelMixin`) and views (`AuthenticatedViewMixin`).
- **Registry Pattern**: `ClassRegistry` facilitates the strategy pattern for dynamic component resolution (e.g., payment gateways).
- **Admin Extensions**: Utilities for multi-tenant admin sites and read-only views.
- **Audit Trails**: Automatic tracking of creation and modification timestamps across all standard models.

## Core Mixins & Helpers
- **`BetterModelMixin`**: Combines UUID primary keys, timestamps, and soft-delete capabilities.
- **`SoftDeleteModelMixin`**: Implements custom logic for marking records as removed without physical deletion.
- **`ClassRegistry`**: A generic tool for registering and retrieving implementation classes by string keys.
- **`ReadOnlyAdmin`**: Disables edit/delete permissions in the Django Admin for specific models.

## Configuration
- No specific configuration required; utilities are designed to be imported and used directly.

## Testing
```bash
# Utilities are tested via the apps that consume them or dedicated unit tests
pytest backend/tests/
```

## Related Documentation
- [Data Model Patterns](../../docs/architecture/data-models.md)
- [Auditing Standards](../../docs/patterns/auditing.md)
