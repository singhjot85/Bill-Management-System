# Services & Orchestration Layer

This directory houses the service and orchestration layers for the BMA backend. It follows a strict separation of concerns to ensure that 3rd-party API logic, business rules, and database operations are decoupled and maintainable.

## Architectural Flow

The system employs a 3-layered architectural approach for handling external integrations and complex business logic:

1.  **Base HTTP Layer (`base.py`)**: A generalized, low-level wrapper around the `requests` library. It manages connection pooling via `requests.Session`, handles base URLs, authentication, and provides standardized logging for all outgoing requests.
2.  **Specific Service Layer (`razorpay_service.py`)**: Inherits from the Base HTTP Layer. It encapsulates logic specific to a single 3rd-party provider (e.g., Razorpay). It handles payload construction, response parsing, and provider-specific security checks (like HMAC signature verification).
3.  **Orchestration Layer (`payment_orchestrator.py`)**: The "brain" of the module. It coordinates between the Specific Service Layer and the Django models. It is responsible for maintaining data integrity, managing database transactions, and executing the high-level business workflow.

### Sequence of Operations (Payment Example)
- **Initiation**: `View` -> `Orchestrator.create_razorpay_order()` -> `RazorpayService.create_order()`.
- **Verification**: `View` -> `Orchestrator.verify_razorpay_payment()` -> `RazorpayService.verify_payment_signature()` -> Database update (Atomic).

## Design Patterns

-   **Service Layer Pattern**: Decouples 3rd-party API logic from Django views and models, making the codebase easier to test and modify.
-   **Orchestrator Pattern**: Centralizes complex workflows that involve multiple models and services into a single coordination point.
-   **Template Method (Base Class)**: `BaseHTTPService` provides a reusable template for any HTTP-based service, ensuring consistent error handling and session management.
-   **Unit of Work**: Utilizes Django's `@transaction.atomic` within the Orchestrator to ensure that multi-step operations (e.g., updating both a Payment and an Invoice) succeed or fail as a single unit.
-   **Pessimistic Locking**: Employs `select_for_update()` during payment verification to prevent race conditions in high-concurrency environments.

## Developer Guide

### Extending the Module
To add a new external service integration:
1.  **Create a new service file**: e.g., `stripe_service.py`.
2.  **Inherit from `BaseHTTPService`**: Implement the provider's specific API methods.
3.  **Update Orchestrator**: Add methods to `PaymentOrchestrator` (or create a new orchestrator) to coordinate the new service with the system's models.

### Usage in Views
Views should **never** call `RazorpayService` or `BaseHTTPService` directly. Always interact through the `PaymentOrchestrator`.

```python
# Correct Usage
orchestrator = PaymentOrchestrator()
payment = orchestrator.create_razorpay_order(invoice_id)
```

### Configuration
Services rely on Django settings for credentials. Ensure that any new service keys are added to `backend/config/settings/` and accessed via `django.conf.settings`.

## Directory Structure

| File | Significance |
| :--- | :--- |
| `base.py` | The foundation for all HTTP-based services. Handles sessions and low-level requests. |
| `razorpay_service.py` | Encapsulates all Razorpay-specific API calls and signature verification. |
| `payment_orchestrator.py` | Coordinates the flow between Razorpay and the `Invoice`/`Payment` models. |
| `__init__.py` | Makes the directory a Python package. |

## Operational Guardrails

-   **Multi-Tenancy**: All database operations within the Orchestrator must respect `django-tenants` boundaries. Ensure the correct tenant is active when calling these services (typically handled by the middleware).
-   **Atomic Transactions**: Any method in the Orchestrator that modifies more than one database record MUST be wrapped in `@transaction.atomic`.
-   **Secret Management**: Never log API keys or secrets. Use the logger cautiously when debugging request/response payloads that might contain PII or tokens.
-   **Signature Verification**: Always verify webhooks or frontend-returned signatures using the service layer's verification methods before updating record statuses.
-   **Error Handling**: Services should raise descriptive exceptions or return boolean success flags that the Orchestrator can use to make decisions. Use `logger.error` for traceability.
