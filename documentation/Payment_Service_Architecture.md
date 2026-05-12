# Payment Service Architecture

This document outlines the architecture and usage of the Payment and Razorpay service layers implemented in `project_apps/services/`.

## Architecture Overview

The payment system follows a layered architecture to ensure separation of concerns, testability, and maintainability.

### 1. Base HTTP Layer (`base.py`)
- **Purpose**: A generalized wrapper around the `requests` library.
- **Features**:
    - Uses `requests.Session` for connection pooling.
    - Centralized handling of base URLs, authentication, and timeouts.
    - Standardized error logging.
- **Why**: Prevents direct `requests` calls throughout the project and allows for easy swapping of the underlying HTTP client if needed.

### 2. Service Layer (`razorpay_service.py`)
- **Purpose**: Encapsulates Razorpay-specific API logic.
- **Key Methods**:
    - `create_order`: Translates application data to Razorpay API format (including paise conversion).
    - `fetch_payment`: Retrieves payment status from Razorpay.
    - `verify_payment_signature`: Securely validates HMAC signatures sent from the frontend.
    - `capture_payment`: Manual capture if required by the flow.

### 3. Orchestration Layer (`payment_orchestrator.py`)
- **Purpose**: Coordinates between external services and the internal Django database.
- **Key Methods**:
    - `create_razorpay_order`: Fetches an Invoice, creates a Razorpay order, and records the initial `Payment` object.
    - `verify_razorpay_payment`: Validates the signature, fetches final details from Razorpay, and atomically updates both `Payment` and `Invoice` statuses within a database transaction.

## Successful Payment Flow (Backend API)

To implement a successful payment flow, follow these steps in your DRF views:

### Step 1: Initiate Payment
When the user clicks "Pay", call the orchestrator to generate a Razorpay Order ID.

```python
from project_apps.services.payment_orchestrator import PaymentOrchestrator

orchestrator = PaymentOrchestrator()
payment_record = orchestrator.create_razorpay_order(invoice_id=invoice_uuid)

# Return payment_record.order_id to the frontend
```

### Step 2: Frontend Checkout
The frontend uses the `order_id` to open the Razorpay Checkout modal. Upon success, Razorpay returns:
- `razorpay_order_id`
- `razorpay_payment_id`
- `razorpay_signature`

### Step 3: Verify and Finalize
The frontend sends these credentials back to a verification endpoint.

```python
from project_apps.services.payment_orchestrator import PaymentOrchestrator

orchestrator = PaymentOrchestrator()
success = orchestrator.verify_razorpay_payment(
    razorpay_order_id=data['razorpay_order_id'],
    razorpay_payment_id=data['razorpay_payment_id'],
    razorpay_signature=data['razorpay_signature'],
    user=request.user
)

if success:
    return Response({"status": "Payment verified and invoice updated."})
```

## Security Implementation
- **Atomic Updates**: Uses `@transaction.atomic` to ensure `Payment` and `Invoice` records stay in sync.
- **Race Condition Protection**: Uses `select_for_update()` on the payment record during verification.
- **Credential Safety**: Credentials are read from environment variables and never logged or stored in the database.
- **Signature Verification**: Signature is computed locally using HMAC-SHA256 to prevent spoofing.
