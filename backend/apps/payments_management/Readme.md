# Payments Management Module

The `payments_management` module is a core tenant-scoped application responsible for handling invoices, payment records, and template management. It integrates with external payment gateways (primarily Razorpay) via a structured service and orchestration layer.

## 1. Architectural Flow

The module follows a strictly decoupled flow to ensure data integrity and security, especially across multi-tenant boundaries.

### Payment Lifecycle
1.  **Invoice Generation**: An `Invoice` is created, linked to a `Customer` and a `Template`.
2.  **Payment Initiation**: When a payment is requested, the `PaymentOrchestrator` is invoked to create a `Payment` record and a corresponding order in the external gateway (e.g., Razorpay).
3.  **Frontend Checkout**: The `order_id` is passed to the frontend to initialize the Razorpay Checkout modal.
4.  **Verification**: Upon successful payment, the frontend sends the gateway credentials (`order_id`, `payment_id`, `signature`) back to the backend.
5.  **Finalization**: The `PaymentOrchestrator` verifies the signature locally and fetches final details from the gateway. If valid, it updates the `Payment` and `Invoice` statuses within a single **atomic transaction**.

## 2. Design Patterns

-   **Orchestrator Pattern**: Centralizes complex logic that coordinates between multiple services (Razorpay) and internal models (`Invoice`, `Payment`). See `backend/apps/services/payment_orchestrator.py`.
-   **Service Layer Pattern**: Encapsulates 3rd-party API logic (signature verification, order creation) into dedicated classes. See `backend/apps/services/razorpay_service.py`.
-   **Mixin Pattern**: Uses `BetterModelMixin` and `VersionedBetterModelMixin` for consistent auditing (UUIDs, timestamps, soft-deletes).
-   **Adapter-like Strategy**: While currently focused on Razorpay, the service layer is designed to be extensible for other gateways by following the `BaseHTTPService` pattern.

## 3. Developer Guide

### Creating an Invoice
Invoices should be created using the `Invoice` model. Ensure a `Customer` and `payable_amount` are provided.
```python
from apps.payments_management.models import Invoice
invoice = Invoice.objects.create(
    customer=customer_obj,
    payable_amount=1000.00,
    status=InvoiceStatusChoices.CREATED
)
```

### Initiating a Payment
Use the `PaymentOrchestrator` to handle order creation and database synchronization.
```python
from apps.services.payment_orchestrator import PaymentOrchestrator
orchestrator = PaymentOrchestrator()
payment_record = orchestrator.create_razorpay_order(invoice_id=invoice.id)
# Return payment_record.order_id to the frontend
```

### Verifying a Payment
Verification must always happen through the orchestrator to ensure local signature checks and atomic updates.
```python
success = orchestrator.verify_razorpay_payment(
    razorpay_order_id=data['order_id'],
    razorpay_payment_id=data['payment_id'],
    razorpay_signature=data['signature'],
    user=request.user
)
```

## 4. Directory Structure & Significance

-   `models.py`: Defines the core data structures:
    -   `Invoice`: Tracks billing details, due dates, and links to customers.
    -   `Payment`: Tracks payment attempts, gateway responses, and verification status.
    -   `Templates`: Manages HTML/Plain-text templates for invoice generation.
-   `apps.py`: Configuration for the Django application.
-   `migrations/`: Standard Django database migration files.
-   `views.py`: (Intended) API ViewSets for payment and invoice endpoints.
-   `admin.py`: Django admin configurations for managing payments/invoices from the dashboard.

## 5. Operational Guardrails

-   **Multi-Tenancy**: All models must inherit from `BetterModelMixin` to ensure isolation within tenant schemas. Never query models without considering the current tenant context.
-   **Atomic Transactions**: Any logic that updates both a `Payment` and an `Invoice` **must** be wrapped in `@transaction.atomic`.
-   **Race Condition Protection**: Use `select_for_update()` when retrieving a `Payment` record for verification to prevent duplicate processing.
-   **Security**: 
    -   Never store or log raw gateway secrets.
    -   Always verify payment signatures locally before updating any record to `PAID` or `COMPLETED`.
    -   The `verified_on`, `verified_by`, and `is_verified` fields are mandatory for successful payment audits.
-   **Service Separation**: Views must never call external APIs directly. All external communication must go through the service layer.
