# Bill Management Application - Data Models
Detailed overview of the database structuring and relationships.

## Core Mixins
All models implement the following mixins (via `BetterModelMixin` or `SafeModelMixin`):
- **UUID Primary Key**: All models use UUIDs instead of auto-incrementing integers.
- **TimeStamps**: `created_at` and `updated_at` fields.
- **Soft Delete**: `is_deleted` flag to prevent accidental data loss.

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
