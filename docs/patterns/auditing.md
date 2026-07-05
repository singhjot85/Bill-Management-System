---
title: Auditing & Base Mixins
type: pattern
app: core
last_updated: 2026-06-15
tags: [models, auditing, soft-delete, versioning]
---

# Auditing & Base Mixins

TL;DR: BMA ensures data integrity and auditability through a suite of model mixins. These provide standardized UUID primary keys, automatic timestamps, soft deletion, and versioning across the entire database schema.

This document covers the core model mixins used to standardize behavior and provide audit trails for all data entities.

## Core Mixins

### 1. `BetterModelMixin`
The standard base for most models. It combines:
- **UUIDModel**: Uses UUID4 as the primary key instead of integers.
- **TimeStampedModel**: Adds `created` and `modified` (AutoCreatedField/AutoLastModifiedField).
- **SoftDeletableModel**: Adds `is_removed` field.

### 2. `SoftDeleteModelMixin`
A more granular soft-delete implementation that tracks *who* deleted the record and *when*.
- `is_removed`: Boolean flag.
- `deleted_at`: Timestamp of deletion.
- `deleted_by`: ForeignKey to the User who performed the action.

### 3. `SimpleVersionModelMixin`
Provides semantic versioning for models that require change tracking (e.g., Templates, Configurations).
- `version_major`, `version_minor`, `version_patch`.
- `version`: A string representation (e.g., "1.2.0").

## Usage Patterns

### Standard Business Entity
Most models should inherit from `BetterModelMixin`.

```python
class Customer(BetterModelMixin):
    name = models.CharField(max_length=255)
    ...
```

### Versioned Configuration
For entities where history and versioning are critical.

```python
class VersionedBetterModelMixin(BetterModelMixin, SimpleVersionModelMixin):
    ...

class NotificationTemplate(VersionedBetterModelMixin):
    ...
```

## Benefits
- **Data Safety**: Soft deletes prevent accidental data loss while keeping the database clean via the `available_objects` manager.
- **Security**: UUIDs prevent ID enumeration attacks.
- **Auditability**: Automatic timestamps and optional deletion tracking provide a clear history of data changes.

---

## Related Documents
- [Data Modeling](../architecture/data-models.md)
- [Multi-Tenancy Architecture](../architecture/multi-tenancy.md)
