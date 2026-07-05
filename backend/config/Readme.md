---
title: Backend Configuration
type: implementation
app: config
last_updated: 2025-01-24
tags: [django, configuration, settings]
---

# Backend Configuration

## Purpose
Central configuration engine for the Bill Management Application (BMA).

This directory manages core infrastructure, multi-tenant orchestration, environment-specific settings, and routing for both public and tenant-specific schemas.

## Quick Start
To add a new application:
1. Open `backend/config/settings/constants.py`.
2. Add the app path to `PROJECT_APPS`.
3. Categorize it under `DJANGO_TENANT_PUBLIC_APPS` or `DJANGO_TENANT_PRIVATE_APPS`.

## Key Concepts
- **Modular Settings**: Configurations are split into `constants.py` (static), `variables.py` (env-driven), and `resolvers.py` (dynamic logic).
- **Resolver Pattern**: Encapsulates complex logic for deriving settings (e.g., DB URLs, cache strings) to prevent circular imports.
- **Tenant Routing**: Uses separate router files (`public_routers.py` vs `routers.py`) to enforce isolation at the URL level.
- **Valkey Integration**: Specialized client configuration for cluster support and performance optimization.

## System-Level Settings
- **`DJANGO_SETTINGS_MODULE`**: Defaults to `config.settings.base`.
- **`MIDDLEWARE`**: Includes `TenantMainMiddleware` for multi-tenant identification.
- **`DATABASE_ROUTERS`**: Set to `django_tenants.routers.TenantSyncRouter`.

## Routing
- **Public Routers**: Handles global APIs like tenant onboarding, user authentication, and system admin.
- **Tenant Routers**: Handles isolated business logic like customer management, invoicing, and payments.

## Testing
```bash
# Verify configuration by running the core test suite
pytest backend/tests/setup/
```

## Related Documentation
- [Architecture Overview](../../docs/architecture/overview.md)
- [Multi-Tenancy Architecture](../../docs/architecture/multi-tenancy.md)
