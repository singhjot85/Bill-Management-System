---
title: Backend Testing Suite
type: implementation
app: tests
last_updated: 2025-01-24
tags: [django, testing, pytest]
---

# Backend Testing Suite

## Purpose
Automated test suite for validating business logic and multi-tenant integrity.

The BMA testing suite prioritizes fast, isolated, and reliable tests using `pytest`. It ensures that tenant data remains isolated and that core features like invoicing and payments function correctly across different schemas.

## Quick Start
```bash
# Run the full suite
pytest

# Run tests for a specific app
pytest backend/tests/customer_management/

# Run with reuse-db to speed up consecutive runs
pytest --reuse-db
```

## Key Concepts
- **Multi-Tenant Isolation**: Tests run in dedicated schemas to verify `django-tenants` boundaries.
- **Eager Tasks**: `CELERY_TASK_ALWAYS_EAGER = True` ensures background tasks run synchronously during tests.
- **Factory-Boy**: Centralized factories (`factories.py`) manage complex test data generation.
- **Given-When-Then**: Standardized test structure for clarity and maintainability.

## Testing Conventions
- **Naming**: `test_subject__condition__result` or `method_name__scenario__expected_behavior`.
- **Isolation**: Tests must not depend on execution order and must clean up after themselves.
- **Mocking**: External APIs and heavy services should be mocked to ensure sub-second unit test execution.
- **Assertions**: Aim for one logical assertion per test to maintain focus.

## Configuration
- **Pytest**: Configured via `pyproject.toml` with strict marker checks and short tracebacks.
- **Settings**: Uses `config.settings.test` which overrides hashers (MD5 for speed) and caches (LocMem).

## Testing
- Automated via CI/CD pipelines.
- Manual execution recommended before every commit using `pytest`.

## Related Documentation
- [Architecture Overview](../../docs/architecture/overview.md)
- [Multi-Tenancy Architecture](../../docs/architecture/multi-tenancy.md)
