# Bill Management Application

## Stack
Django + DRF + django-tenants + Celery + Valkey | Vue 3 + Vite | PostgreSQL | Docker

## Architecture
- `auth` → public schema only. `customer_management`, `payments_management` → tenant-scoped
- All models MUST inherit SoftDelete + Timestamp mixins (not listed in specs, but required)
- Payment → Invoice is one-directional (Invoice does NOT reference Payment)
- Tenant invoice numbers: `INV-YYYY-NNNN`, sequential per tenant
- Template keys: snake_case, unique per tenant

## API Rules
- DRF serializers in `serializers.py`, viewsets in `views.py`, URLs in `urls.py` per app
- Vue frontend consumes DRF endpoints only — no mixed template rendering for new features

## Business Logic
- Invoice status transitions: validate atomically
- Payment verification sets `verified_on`, `verified_by`, `verified_flag` together
- Store raw payment response in `raw_payment_responses`, parsed in `details`. Never log signatures

## Async & Files
- PDF generation, emails, payment verification → always via Celery tasks
- `document_url` on Invoice → tenant-scoped storage
- Templates cached in Valkey (1hr), PDFs cached by content hash (24hr)

## Dev Workflow
- `poetry lock` before committing dependency changes
- Pre-commit: linting, formatting, import sorting
- Test target: 80%+ coverage. Multi-tenant isolation tests required
