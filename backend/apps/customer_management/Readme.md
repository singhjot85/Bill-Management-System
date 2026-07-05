---
title: Customer Management
type: implementation
app: customer_management
last_updated: 2026-06-15
tags: [django, customer_management, onboarding]
---

# Customer Management

## Purpose
The `customer_management` module is a core component of the Bill Management Application (BMA), responsible for managing customer profiles, addresses, and orchestrating the public-facing checkout workflows.

It acts as the primary interface for public users (unauthenticated) to enter the system, handling identity validation, payment initiation, and unified form submission.

## Quick Start
To initialize the module within a tenant context:
```bash
python manage.py migrate
```

## Key Concepts
- **Identity Validation**: Public users trigger email and phone validation via stubs that simulate delivery.
- **Unified Submission**: The `FormSubmitSerializer` orchestrates an atomic operation across `Customer`, `CustomerAddress`, `Invoice`, and `Payment` models.
- **Invoice Lookup**: Users can retrieve their generated invoices using a unique tracking code.
- **Orchestration Serializer**: Implements the "Service Layer" pattern within a serializer for cohesive business processes.

## API Reference
| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/workflow/validate_email/` | POST | Triggers email validation (asynchronous stub) |
| `/api/workflow/validate_phone/` | POST | Triggers phone validation (asynchronous stub) |
| `/api/workflow/make_payment/` | POST | Creates a payment record/intent |
| `/api/workflow/submit_form/` | POST | Atomic creation of customer, address, and invoice |
| `/api/workflow/invoice/{code}/` | GET | Retrieves invoice details by unique code |

## Configuration
This app relies on standard multi-tenant settings. Ensure `django-tenants` is correctly configured in `backend/config/settings/`.

## Testing
To run tests for this module:
```bash
pytest backend/tests/customer_management/
```

## Related Documentation
- [Architecture Overview](../../../docs/architecture/overview.md)
- [Data Models](../../../docs/architecture/data-models.md)
- [Multi-Tenancy Guide](../../../docs/architecture/multi-tenancy.md)
