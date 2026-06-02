# Backend Testing Suite

This directory contains the automated test suite for the BMA backend. We prioritize fast, isolated, and reliable tests that validate both business logic and multi-tenant integrity.

## Core Tooling Stack

- **[pytest](https://docs.pytest.org/)**: Our primary test framework. Chosen for its concise syntax, powerful fixture system, and superior output compared to Django's built-in `unittest` wrapper.
- **[pytest-django](https://pytest-django.readthedocs.io/)**: Provides seamless Django integration, handling database setup, tenant synchronization, and useful fixtures like `db` and `client`.
- **[factory-boy](https://factoryboy.readthedocs.io/)**: Used for generating test data. Factories provide a clean, reusable way to create complex model instances and their relationships without the boilerplate of manual `Model.objects.create()` calls.

## Intentional Omissions (Rationale)

To maintain a lean and fast testing environment, we have intentionally deferred or bypassed certain common tools:

- **`pytest-celery`**: Skipped in favor of `CELERY_TASK_ALWAYS_EAGER = True`. This executes tasks synchronously within the test process, simplifying debugging and removing the need for a running worker/broker during tests.
- **`pytest-xdist`**: Parallel execution is currently unnecessary due to the suite's size. We prioritize simplicity over the overhead of managing parallel test state.
- **`pytest-cov`**: While we track coverage informally, we avoid strict enforcement to focus on testing critical business paths and multi-tenant isolation rather than chasing arbitrary percentage targets.

## Directory Organization

The test suite mirrors the structure of the `apps/` directory to ensure discoverability:

```text
backend/tests/
├── conftest.py          # Project-wide fixtures and pytest configuration
├── factories.py         # Centralized factory-boy definitions
├── customer_management/ # App-specific tests
│   ├── __init__.py      # Required for proper module resolution
│   ├── conftest.py      # App-level fixtures (e.g., specific tenant setups)
│   ├── test_models.py
│   └── test_views.py
└── tenants/             # Multi-tenant isolation and provisioning tests
```

## Configuration (via `pyproject.toml`)

We utilize `pyproject.toml` for pytest configuration to keep the root directory clean. Key settings include:

- **`addopts`**:
    - `--strict-markers`: Raises an error if an unregistered marker is used, preventing silent typos.
    - `--tb=short`: Streamlines failure output to focus on the immediate traceback.
    - `--reuse-db`: Speeds up local runs by persisting the test database between sessions.
    - `--import-mode=importlib`: Ensures reliable module discovery across nested directories.
- **`python_files`**: Configured to scan for `test_*.py` patterns.

## Performance & Isolation Strategies

### 1. Multi-Tenant Database Isolation
Tests run in a dedicated test database to ensure total isolation from development data. This is critical for `django-tenants`, as it allows schema-level operations (creation, migration, deletion) to happen safely during the test lifecycle.

### 2. Synchronous Task Execution
By setting `CELERY_TASK_ALWAYS_EAGER = True`, we ensure that background tasks (like PDF generation or email dispatch) run immediately. This allows tests to assert the results of these tasks (e.g., file creation) without complex asynchronous synchronization.

### 3. Fast Password Hashing
We override the default password hashers to use **MD5** during tests. While insecure for production, it is significantly faster than BCrypt or Argon2, saving ~0.5s per user creation and drastically reducing the total suite runtime.

### 4. Memory-Based Caching
We use `LocMemCache` for testing. This removes the dependency on an external Valkey/Redis instance while maintaining the speed and reliability of cache-related logic verification.
