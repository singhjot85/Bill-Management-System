# AGENTS.md

## Project: Bill Management Application
A system that can be used to generate and manage bills/invoices.

### Core Rules (Always Follow)

1. **Multi-Tenant Architecture**
   - `tenants` app lives in **public schema** only
   - `customer_management`, `payments_management` are **tenant-scoped**
   - `setup` is a shared app that will be in both **public schema** and **tenant-scoped**.
   - Always use `django-tenants` utilities for tenant-aware queries

2. **Model Conventions (Mandatory)**
   - ALL models MUST inherit from mixins defined in `utils/model_utils.py` mixins (not listed in specs, but required)
   - Foreign keys follow the exact relationships defined in specs — do not add/remove without discussion

3. **API & Frontend Separation**
   - DRF serializers in each app's `serializers.py`
   - Viewsets/APIViews in `views.py`.
   - URL conf in `config/public_routers.py` for **public schema** and `config/routers.py` for **tenant-scoped**.
   - ONLY use custom admin sites in `utils/admin_utils/`, DO NOT use django's `admin.sites`.
   - Vue frontend consumes DRF endpoints only — no mixed template rendering for new features

4. **Validation & Business Logic**
   - Invoice status transitions must be validated
   - Payment verification sets `verified_on`, `verified_by`, `verified_flag` atomically
   - Customer types (`PUBLIC/PRIVATE/VIP/CORPORATE`) determine feature flags — enforce in backend

5. **File Handling**
   - `document_url` on Invoice uses Django's FileField — store in tenant-scoped storage
   - Invoice generation creates both PDF and stores in `context_data` as JSON backup

6. **Async Tasks**
   - Invoice PDF generation, email sending, payment gateway verification → always via Celery tasks
   - Use `django-celery-beat` for recurring tasks only (e.g., due date reminders)

7. **Naming Consistency**
   - Tenant invoice numbers: `INV-YYYY-NNNN` format, sequential per tenant
   - Template keys: snake_case, unique per tenant
   - URL routes: RESTful, app namespaced (`customer_management:address-list`)

8. **Development Workflow**
   - Add runtime creds in .env/ and also update an appropriate example file.
   - `compose/` contains all the docker realted settings, each service in seperate directory.
   - Only bake what is required in the image, don't make it bulky.
   - `config/` contains the project configuration settings.
   - `backend/apps` consist all the project applications.
   - Run `poetry lock` before committing dependency changes
   - Pre-commit hooks run: linting, formatting, import sorting

### Quick Decision Reference

- **New field needed?** → Add to existing model or create new model? Discuss first.
- **New app?** → Tenant-scoped unless it's authentication/shared infra.
- **Payment integration?** → Store raw response in `raw_payment_responses`, parsed summary in `details`. Never log signatures.

### Dynamic Form Workflow Notes

- Tenant-scoped public workflow endpoints live in `config/routers.py` and should stay DRF-only:
  - `validate_email/` queues/sends validation email.
  - `validate_phone/` queues/sends validation message.
  - `make_payment/` creates the app payment record, calls the gateway, and returns the app `payment_id`.
  - `submit_form/` wraps customer creation and invoice initiation in a single database transaction.
  - `invoice/<code>/` fetches invoice state by the returned unique invoice code.
- Current email, phone, payment gateway, and backend-process dispatch implementations are intentionally small stubs; replace them with Celery/provider integrations without changing the endpoint contract.
- `submit_form/` must be idempotent when a returned invoice code is supplied again, so retries can reuse a code instead of creating duplicate customers/invoices.
