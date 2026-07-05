---
title: Razorpay Integration Spec
type: integration
app: core
last_updated: 2026-06-15
tags: [razorpay, payments, integration, security]
---

# Razorpay Integration Spec

TL;DR: The Razorpay integration enables secure payment processing through strict data structures (dataclasses) and signature verification. It supports order creation, payment capture, and automated verification flows within a multi-tenant environment.

This document covers the payload structures, backend endpoints, and the successful payment integration flow for Razorpay.

## Data Structures

We use Python dataclasses to ensure strict type safety for all communication with Razorpay.

### 1. Order Creation Request
Sent to initialize a payment and receive a `razorpay_order_id`.

```python
@dataclass
class RazorpayOrderRequest:
    amount: int  # In smallest currency unit (e.g., paise)
    currency: str = "INR"
    receipt: Optional[str] = None
    notes: Dict[str, Any] = field(default_factory=dict)
```

### 2. Signature Verification Payload
Data received from the frontend checkout for backend validation.

```python
@dataclass
class RazorpayVerificationPayload:
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
```

## Backend Endpoints (Tenant Scoped)

### 1. Invoice Retrieval
- **Endpoint**: `GET /invoice/<invoice_code>/`
- **Description**: Fetches detailed information about an invoice and its customer.

### 2. Payment Initiation
- **Endpoint**: `POST /make_payment/`
- **Description**: Initiates a payment record and returns the `order_id` from Razorpay.

### 3. Verification
Integrated into the orchestrator logic, triggered by frontend callbacks to ensure the payment is legitimate before updating internal records.

## Integration Flow Summary
1. **Identify**: Fetch invoice details via `GET /invoice/<code:str>/`.
2. **Initialize**: Call `POST /make_payment/` to get an `order_id`.
3. **Checkout**: Open the Razorpay Checkout modal on the frontend.
4. **Verify**: Send `payment_id` and `signature` to the backend for HMAC-SHA256 verification and atomic status updates.

---

## Related Documents
- [Payment Service Architecture](../patterns/payments.md)
- [Frontend Architecture](../architecture/frontend.md)
- [Data Modeling](../architecture/data-models.md)
