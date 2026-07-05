---
title: Data Modeling
type: architecture
app: core
last_updated: 2026-06-15
tags: [models, database, postgresql, schemas]
---

# Data Modeling

TL;DR: BMA's data model is split between the public schema (tenant management) and tenant schemas (business operations). It uses UUIDs, soft deletes, and timestamps across all entities to ensure auditability and data integrity.

This document covers the database structure, core mixins, and detailed field-level specifications for all models in the system.

## Core Mixins

All models implement the following mixins (via `BetterModelMixin` or `SafeModelMixin`):

-   **UUID Primary Key**: Most models use UUIDs instead of auto-incrementing integers.
-   **TimeStamps**: `created` and `modified` (via `TimeStampedModel`) or custom `created_at`/`updated_at`.
-   **Soft Delete**: `is_removed` (via `SoftDeletableModel`) or `is_deleted`.

---

## 🏗️ Public Schema Models

These models are global and reside in the `public` schema.

### [Tenants] `apps.tenants`
Manages the multi-tenant infrastructure and organization-level metadata.

#### `OrganizationTenant`
- **Significance**: Core tenant entity required by `django-tenants`.
- **Fields**:
  - `id`: UUID (SafeModelMixin)
  - `name`: Tenant display name (CharField)
  - `schema_name`: Database schema identifier (CharField, Unique)
  - `in_production`: Environment status (BooleanField)
- **References**:
  - `OrganizationDomain` (1-M): One tenant can have multiple domains.

#### `OrganizationDomain`
- **Significance**: Maps hostnames to specific tenants.
- **Fields**:
  - `domain`: Fully qualified domain name (CharField, Unique)
  - `tenant`: (M-1) ForeignKey to `OrganizationTenant`
  - `is_primary`: Boolean flag identifying the primary domain.

#### `OrganizationBranding`
- **Significance**: Customizes the UI/UX and contact details for a specific organization.
- **Fields**:
  - `organization`: (1-1) OneToOneField to `OrganizationTenant`
  - `country`: Organization country (ChoiceField)
  - `phone`: Organization contact phone (CharField)
  - `email`: Organization contact email (CharField)
  - `navbar_icon`: Icon for the top navigation (CharField/Path)
  - `navbar_title`: Title for the top navigation (CharField)
  - `footer_icon`: Icon displayed in the footer (CharField)
  - `footer_text`: Main text for the footer (TextField)
  - `footer_extra_text`: Additional text at the end of the footer (TextField)
  - `version`: (SimpleVersionModelMixin) Semantic versioning fields.

---

## 🏢 Tenant Schema Models

These models are isolated within each tenant's private database schema.

### [Customer Management] `apps.customer_management`
Handles the entities being billed.

#### `Customer`
- **Significance**: Represents a person or organization that receives invoices.
- **Fields**:
  - `id`: UUID (BetterModelMixin)
  - `name`: Customer name (CharField)
  - `phone`: Mobile number (CharField)
  - `email`: Contact email (EmailField)
  - `is_phone_verified`: Mobile verification status (BooleanField)
  - `is_email_verified`: Email verification status (BooleanField)
  - `source`: Where the customer originated (TextField)
  - `customer_type`: `PUBLIC`, `PRIVATE`, or `INTERNAL` (ChoiceField)
  - `external_reference`: External system mapping ID (CharField)
  - `details`: Flexible metadata storage (JSONField)
- **References**:
  - `CustomerAddress` (1-M): One customer can have many addresses.

#### `CustomerAddress`
- **Significance**: Shipping or billing address for a customer.
- **Fields**:
  - `customer`: (M-1) ForeignKey to `Customer`.
  - `address_line_1`, `address_line_2`: Street details (CharField)
  - `city`: City name (CharField)
  - `country`: Country name (CharField)
  - `postal_code`: Area code (IntegerField)
  - `is_primary`: Flags the default billing address (BooleanField)

### [Payments & Invoicing] `apps.payments_management`
Core business logic for revenue collection.

#### `Invoice`
- **Significance**: The primary billing document issued to customers.
- **Fields**:
  - `invoice_number`: Unique generated code (CharField, Unique) e.g., `INV-2026-XXXX`.
  - `invoice_date`: Date the invoice was issued (DateField)
  - `due_date`: Date the payment is due (DateField)
  - `status`: `CREATED`, `PAID`, `DEFAULTED`, `INVALID` (ChoiceField)
  - `document`: Path to the generated PDF (FileField)
  - `context_data`: Snapshot of data used for template rendering (JSONField)
  - `payable_amount`: Total amount to be paid (FloatField)
  - `amount_paid`: Total amount received (FloatField)
- **References**:
  - `customer`: (M-1) ForeignKey to `Customer`.
  - `generated_by`: (M-1) ForeignKey to `User`.
  - `template`: (M-1) ForeignKey to `Templates`.

#### `Templates`
- **Significance**: Stores HTML/Text source for invoice generation.
- **Fields**:
  - `template_name`: Human-readable name (CharField)
  - `template_type`: e.g., `DEFAULT_INVOICE` (ChoiceField)
  - `is_active`: Toggle for availability (BooleanField)
  - `html`: HTML source for PDF generation (TextField)
  - `plain_text`: Text-only fallback content (TextField)
  - `version`: (VersionedBetterModelMixin) Full semantic versioning.

#### `Payment`
- **Significance**: Records of financial transactions via external gateways.
- **Fields**:
  - `status`: `CREATED`, `PROCESSING`, `COMPLETED`, `FAILED` (ChoiceField)
  - `payment_type`: Description of payment (CharField)
  - `order_id`: Gateway Order ID (CharField)
  - `payment_id`: Gateway Payment ID (CharField)
  - `amount`: Transaction value (FloatField)
  - `currency`: Transaction currency (ChoiceField)
  - `raw_payment_response`: Full payload from the gateway (JSONField)
  - `gateway_name`: `RAZORPAY`, `PAYPAL` (ChoiceField)
  - `gateway_signature`: Verification signature (CharField)
  - `is_verified`: Audit field for signature check (BooleanField)
  - `verified_on`: Timestamp of verification (DateTimeField)
- **References**:
  - `invoice`: (M-1) ForeignKey to `Invoice`.
  - `payee`: (M-1) ForeignKey to `Customer`.
  - `verified_by`: (M-1) ForeignKey to `User`.

### [Notifications] `apps.notifications`
Event-driven communication system.

#### `NotificationTemplate`
- **Significance**: Reusable content for different channels and events.
- **Fields**:
  - `template_name`: Unique template identifier (ChoiceField)
  - `event_type`: Triggering event type (ChoiceField)
  - `channel`: `EMAIL`, `SMS`, `WEBHOOK`, `PUSH` (ChoiceField)
  - `language`: Content language code (ChoiceField)
  - `subject`: Notification subject line (TextField)
  - `plain_text`: Main content for SMS/Plain-text email (TextField)
  - `html`: Content for HTML email (TextField)
- **References**:
  - `NotificationLog` (1-M): Tracks history of usage.

#### `NotificationLog`
- **Significance**: Detailed audit trail for every notification sent.
- **Fields**:
  - `status`: `QUEUED`, `SENT`, `FAILED`, `BOUNCED` (ChoiceField)
  - `task_id`: Celery task identifier (CharField)
  - `channel`: Delivery channel used (ChoiceField)
  - `template_snapshot`: Rendered content at time of send (TextField)
  - `context_data`: Variables used for rendering (JSONField)
  - `errors`: Traceback or provider error messages (TextField)
- **References**:
  - `template`: (M-1) ForeignKey to `NotificationTemplate`.

#### `NotificationPreferences`
- **Significance**: User/Customer opt-in/opt-out settings.
- **Fields**:
  - `event_type`: Per-event granularity (ChoiceField)
  - `opted_email`: (BooleanField)
  - `opted_sms`: (BooleanField)
  - `opted_webhook`: (BooleanField)
  - `opted_push_notification`: (BooleanField)
- **References**:
  - `user`: (1-1) OneToOneField to `User`.
  - `customer`: (1-1) OneToOneField to `Customer`.

### [Setup] `apps.setup`
Dynamic system configurations.

#### `Configurations`
- **Significance**: Stores versioned JSON configurations (e.g., API keys, feature flags).
- **Fields**:
  - `interface_type`: Identifier for the setting (ChoiceField)
  - `details`: Key-value configuration pairs (JSONField)
  - `version`: (VersionedBetterModelMixin) Supports rollback and version tracking.

---

## Related Documents
- [Multi-Tenancy Strategy](./multi-tenancy.md)
- [Auditing & Base Mixins](../patterns/auditing.md)
- [Asynchronous Task System](./async-system.md)
