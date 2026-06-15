# Customer Management Module

The `customer_management` module is a core component of the Bill Management Application (BMA), responsible for managing customer profiles, addresses, and orchestrating the public-facing checkout workflows.

## 1. Architectural Flow

This module acts as the primary interface for public users (unauthenticated) to enter the system. The logic flows as follows:

1.  **Identity Validation**: Public users can trigger email and phone validation via the `WorkflowViewSet`. Currently, these are implemented as asynchronous stubs that simulate validation delivery.
2.  **Payment Initiation**: Before final submission, a payment record is typically created using the `make_payment` action, which interacts with the `payments_management` app.
3.  **Unified Submission**: The `submit_form` action uses the `FormSubmitSerializer` to perform a complex, atomic operation:
    -   Creates or retrieves a `Customer`.
    -   Creates a `CustomerAddress`.
    -   Generates an `Invoice` (linked to `payments_management`).
    -   Links any pre-existing `Payment` to the new `Customer` and `Invoice`.
4.  **Retrieval**: Users can lookup their generated invoices using a unique code via the `invoice` action.

## 2. Design Patterns

*   **Orchestration Serializer**: The `FormSubmitSerializer` implements the "Service Layer" pattern within a serializer. It coordinates multiple models across different apps (`Customer`, `CustomerAddress`, `Invoice`, `Payment`) to ensure a cohesive business process.
*   **Atomic Transactions**: All multi-model mutations in `FormSubmitSerializer` are wrapped in `@transaction.atomic` to guarantee data integrity.
*   **Mixin Pattern**: Models inherit from `BetterModelMixin`, providing standardized UUID primary keys, timestamps, and soft-delete capabilities.
*   **Action-Based ViewSets**: Instead of standard CRUD, the `WorkflowViewSet` uses DRF `@action` decorators to expose granular, workflow-specific endpoints (`validate_email`, `submit_form`, etc.).

## 3. Developer Guide

### Extending Customer Profiles
To add new fields to a customer (e.g., TAX ID, Date of Birth):
1.  Modify `Customer` in `models.py`.
2.  Run `makemigrations` and `migrate`.
3.  Update `FormSubmitSerializer` in `serializers.py` to handle the new data during creation.

### Modifying the Checkout Workflow
The checkout flow is centralized in `WorkflowViewSet`. If you need to add a new step (e.g., Terms of Service acceptance):
1.  Add a new `@action` in `WorkflowViewSet`.
2.  If the step involves saving data, update the `FormSubmitSerializer` or create a new dedicated serializer.

### Validation Logic
Currently, `send_validation_email` and `send_validation_message` in `views.py` are stubs. To implement real validation:
1.  Integrate with a service (e.g., AWS SES, Twilio).
2.  Ideally, move this logic to a dedicated service layer in `apps/services/`.

## 4. Directory Structure

*   `admin.py`: Registers `Customer` and `CustomerAddress` with the Django admin interface.
*   `apps.py`: App configuration and name definition.
*   `models.py`: Defines the core data structures: `Customer` and `CustomerAddress`.
*   `serializers.py`: Contains both data-transfer objects (DTOs) and orchestration logic (`FormSubmitSerializer`).
*   `views.py`: Implements the `WorkflowViewSet` which houses the public API endpoints.
*   `migrations/`: Standard Django database migration history.

## 5. Operational Guardrails

*   **Multi-Tenancy**: This is a tenant-scoped app. Never query `Customer` models without ensuring the tenant context is correctly set (handled automatically by `django-tenants` in most cases).
*   **Soft Delete**: Be aware that models use soft-delete. Use `.available_objects` if you want to exclude deleted records, or `.objects` if you need everything.
*   **Atomic Operations**: Always use `@transaction.atomic` when a single API call modifies multiple related models to prevent partial data states.
*   **Service Layer Boundary**: While some logic exists in serializers for brevity, complex 3rd-party integrations (like SMS/Email gateways) should be moved to the dedicated service layer as per `AGENTS.md`.
