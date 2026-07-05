---
title: Multi-Tenancy Architecture
type: architecture
app: core
last_updated: 2026-06-15
tags: [multi-tenancy, django-tenants, isolation]
---

# Multi-Tenancy Architecture

TL;DR: BMA implements multi-tenancy using a shared-database, isolated-schema approach via `django-tenants`. This ensures strict data segregation between organizations while maintaining resource efficiency.

This document covers the implementation details of the multi-tenancy model in BMA, including schema isolation and data management.

## Implementation: Shared-DB, Isolated-Schema

BMA utilizes `django-tenants` to manage data isolation at the database level.

### 1. Public Schema
The public schema houses platform-wide data that is shared across all tenants:
- **Tenant Metadata**: `OrganizationTenant` model which defines the schema name and production status.
- **Global User Accounts**: Shared authentication system.
- **Shared Configurations**: Global defaults and system-wide settings.

### 2. Tenant Schemas
Every organization (tenant) receives a dedicated database schema.
- **Isolation**: All customer data, invoices, and payments are stored here.
- **Security**: No cross-tenant data leakage is possible as queries are restricted to the active schema by the `django-tenants` middleware.
- **Customization**: Allows for tenant-specific data structures and configurations without affecting others.

## Tenant-Scoped Models
Models defined in tenant-bound apps are automatically migrated to each tenant's schema. This includes:
- `Customer Management`: Customers, addresses.
- `Payments & Invoicing`: Invoices, payments, templates.
- `Setup`: Tenant-specific configurations.

---

## Related Documents
- [Architectural Overview](./overview.md)
- [Data Modeling](./data-models.md)
