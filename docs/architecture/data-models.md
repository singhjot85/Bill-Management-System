---
title: Data Modeling
type: architecture
app: core
last_updated: 2026-06-15
tags: [models, database, postgresql, schemas]
---

# Data Modeling

TL;DR: BMA's data model is split between the public schema (tenant management) and tenant schemas (business operations). It uses UUIDs, soft deletes, and timestamps across all entities to ensure auditability and data integrity.

This document covers the database structure, core mixins, and relationships between entities in both public and tenant schemas.

## Core Mixins
All models implement the following mixins (via `BetterModelMixin` or `SafeModelMixin`):
- **UUID Primary Key**: All models use UUIDs instead of auto-incrementing integers for enhanced security and distributed system compatibility.
- **TimeStamps**: `created_at` and `updated_at` (or `created` and `modified`) fields.
- **Soft Delete**: `is_removed` flag to prevent accidental data loss.

See [Auditing & Base Mixins](../patterns/auditing.md) for implementation details.

---

## Tenants (Public Schema)

### OrganizationTenant
- `name`: Display name of the tenant.
- `schema_name`: Database schema identifier (e.g., `acme_corp`).
- `in_production`: Boolean flag for environment status.

### OrganizationBranding
- `organization`: 1:1 link to `OrganizationTenant`.
- `navbar_title`, `navbar_icon`: Customizes the header.
- `footer_text`, `footer_extra_text`, `footer_icon`: Customizes the footer.
- `phone`, `email`, `country`: Tenant contact details.

---

## Customer Management (Tenant Schema)

### Customer
- `name`, `phone`, `email`: Contact details.
- `customer_type`: `PUBLIC`, `PRIVATE`, or `INTERNAL`.
- `is_phone_verified`, `is_email_verified`: Verification flags.
- `external_reference`: Link to external systems.
- `details`: JSON field for arbitrary metadata.

### CustomerAddress
- `customer`: FK to `Customer`.
- `address_line_1`, `address_line_2`, `city`, `country`, `postal_code`.
- `is_primary`: Boolean to identify the main billing address.

---

## Payments & Invoicing (Tenant Schema)

### Invoice
- `invoice_number`: Unique generated code (e.g., `INV-2026-XXXX`).
- `invoice_date`, `due_date`: Key billing dates.
- `status`: `CREATED`, `PAID`, `DEFAULTED`, `INVALID`.
- `payable_amount`, `amount_paid`: Financial tracking.
- `document`: FileField for the generated PDF.
- `context_data`: JSON field storing data used to render the template.
- **Relationships**:
  - `customer`: FK to `Customer`.
  - `generated_by`: FK to `User`.
  - `template`: FK to `Templates`.

### Templates
- `template_name`: Human-readable name.
- `template_type`: `DEFAULT_INVOICE`, etc.
- `html`, `plain_text`: The template source code.
- `is_active`: Toggle for template availability.

### Payment
- `order_id`: Razorpay Order ID.
- `payment_id`: Razorpay Payment ID.
- `amount`, `currency`: Transaction value.
- `status`: `CREATED`, `PROCESSING`, `COMPLETED`, `FAILED`.
- `gateway_name`: `RAZORPAY`, `PAYPAL`.
- `is_verified`, `verified_on`, `verified_by`: Audit trail for verification.
- **Relationships**:
  - `invoice`: FK to `Invoice`.
  - `payee`: FK to `Customer`.
  - `verified_by`: FK to `User`.

---

## Setup (Tenant Schema)

### Configurations
- `interface_type`: Identifier for the setting (e.g., `RAZORPAY_CONFIG`).
- `details`: JSON field storing the actual configuration values.

---

## Related Documents
- [Multi-Tenancy](./multi-tenancy.md)
- [Auditing & Base Mixins](../patterns/auditing.md)
