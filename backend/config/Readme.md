# Backend Configuration Module (`backend/config/`)

This directory serves as the central configuration engine for the Bill Management Application (BMA). It manages core infrastructure, multi-tenant orchestration, asynchronous task processing, and environment-specific settings.

## 1. Architectural Flow

The configuration module is designed to support a multi-tenant architecture using `django-tenants`. The flow of data and logic through this module follows these steps:

1.  **Initialization**: Upon startup, `manage.py` or `wsgi.py` sets the `DJANGO_SETTINGS_MODULE` to `config.settings.base`.
2.  **Modular Settings Loading**: `config.settings.base` aggregates configurations from `constants.py` (static), `variables.py` (environment-driven), and `resolvers.py` (dynamic logic).
3.  **Tenant Identification**: The `TenantMainMiddleware` (configured in `base.py`) intercepts incoming requests to identify the tenant schema based on the hostname.
4.  **Dynamic Routing**:
    *   Requests to the **Public Schema** (e.g., system admin, tenant onboarding) use `config.public_routers.py`.
    *   Requests to a **Tenant Schema** (e.g., customer management, payments) use `config.routers.py`.
5.  **Async Orchestration**: `config.celery.py` initializes a `TenantAwareCeleryApp`, ensuring that background tasks (PDF generation, emails) are executed within the correct tenant context.

## 2. Design Patterns

*   **Modular Configuration**: Instead of a monolithic `settings.py`, configurations are split by their nature (constants vs. variables) to improve maintainability and security.
*   **Resolver Pattern**: Complex setting derivations (like cache/broker URLs or provider-specific options) are encapsulated in `resolvers.py`. This prevents circular imports and keeps `base.py` declarative.
*   **Tenant-Aware Task Queueing**: The use of a specialized Celery app class ensures that tenant schema information is propagated to worker processes.
*   **Patched Client Pattern**: `valkey_cluster_client.py` uses a monkey-patch/override strategy to extend the functionality of the base Valkey client to support `set_many` with timeouts, as required by `django-constance`.

## 3. Developer Guide

### Adding a New Application
When adding a new Django app to the project, update `backend/config/settings/constants.py`:
1.  Add the app path (e.g., `apps.new_feature`) to `PROJECT_APPS`.
2.  If it should be available in the shared public schema, add it to `DJANGO_TENANT_PUBLIC_APPS`.
3.  If it is tenant-specific, add it to `DJANGO_TENANT_PRIVATE_APPS`.

### Extending Settings
*   **Static values** (e.g., default pagination size): Add to `constants.py`.
*   **Environment variables**: Add to `variables.py` using `os.getenv`.
*   **Complex logic**: Add a function in `resolvers.py` and call it from `base.py`.

### Routing
*   Public-facing APIs or Admin sites should be registered in `public_routers.py`.
*   Tenant-specific business logic APIs should be registered in `routers.py`.

## 4. Directory Structure & Significance

```text
backend/config/
├── settings/               # Modularized Django settings
│   ├── base.py             # Main entry point; aggregates all settings.
│   ├── constants.py        # Static configurations (app lists, model labels, defaults).
│   ├── variables.py        # Environment-driven variables (DB, Cache, Secrets).
│   ├── resolvers.py        # Logic for resolving complex or dynamic settings.
│   └── test.py             # Settings overrides for pytest suite.
├── celery.py               # Celery app initialization (tenant-aware).
├── beat.py                 # Celery Beat scheduler configuration.
├── public_routers.py       # URL routing for the public/shared schema.
├── routers.py              # URL routing for isolated tenant schemas.
├── valkey_cluster_client.py # Custom patch for Valkey (Cache/Broker) cluster support.
├── wsgi.py                 # WSGI application entry point for production servers.
└── __init__.py             # Makes the directory a Python package.
```

## 5. Operational Guardrails

*   **No Business Logic**: Never place business logic or model imports inside the `config/` directory (except for setting resolvers).
*   **Security First**: Never hardcode secrets in `constants.py` or `base.py`. Use `variables.py` to pull from environment variables.
*   **Circular Imports**: Avoid importing `django.conf.settings` inside `resolvers.py` or `variables.py`. These files are imported *by* the settings initialization process.
*   **Tenant Isolation**: When adding new middlewares or routers, always verify that they respect the tenant boundaries defined by `django-tenants`.
*   **Valkey Over Redis**: The project uses Valkey as the primary caching and message broker layer. Ensure any infrastructure changes are compatible with Valkey.
