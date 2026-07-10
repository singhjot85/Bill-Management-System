---
title: Tenants Management
type: implementation
app: tenants
last_updated: 2025-01-24
tags: [django, tenants, multi-tenancy]
---

# Tenants Management

## Purpose
Core foundation for the multi-tenant architecture of the Bill Management System (BMA).

This module leverages `django-tenants` to provide schema-level isolation for different organizations. It manages the lifecycle of tenants, their domains, and tenant-specific branding while maintaining a shared public schema for global data like users and organization registries.

## Quick Start
To onboard a new organization:
1. Create an `OrganizationTenant` record with a unique `schema_name`.
2. Create an `OrganizationDomain` record pointing to that tenant.
3. (Optional) Initialize `OrganizationBranding` to customize the tenant's UI.

## Key Concepts
- **Schema Isolation**: Database-level separation ensures strict data boundaries between organizations.
- **Public Schema**: Contains global models (`OrganizationTenant`, `OrganizationDomain`, `User`) accessible across all tenants.
- **Tenant Schemas**: Contains isolated data (customers, invoices, notifications).
- **Request Routing**: `TenantMainMiddleware` identifies the tenant via the hostname and sets the PostgreSQL search path.
- **Singleton Branding**: Each tenant is linked to a unique `OrganizationBranding` record for UI customization.

## API Reference
| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/auth/login/` | POST | Authenticate a user. |
| `/api/auth/logout/` | POST | Terminate the current session. |
| `/api/auth/me/` | GET | Retrieve details of the authenticated user. |
| `/api/branding/` | GET | Retrieve UI configuration for the current tenant. |

## Configuration
- `TENANT_MODEL`: Must be set to `tenants.OrganizationTenant`.
- `TENANT_DOMAIN_MODEL`: Must be set to `tenants.OrganizationDomain`.
- `SHARED_APPS`: Includes this app to ensure it resides in the `public` schema.
- `REST_FRAMEWORK` (in settings): TokenAuthentication and SessionAuthentication are enabled to support client authentication.

## Testing
```bash
# Run tenant-specific tests
pytest backend/tests/tenants/
```

## Related Documentation
- [Multi-Tenancy Architecture](../../../docs/architecture/multi-tenancy.md)
- [Data Models](../../../docs/architecture/data-models.md)
