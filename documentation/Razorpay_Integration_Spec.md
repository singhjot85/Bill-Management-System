# Razorpay Integration Specification

This document defines the data structures used for communicating with Razorpay and the available backend API endpoints.

## 1. Razorpay API Payload Structures

We use Python dataclasses to define the strict structure of data sent to the generalized HTTP wrapper and then to Razorpay.

### A. Order Creation Request
Sent when initializing a payment flow to get a `razorpay_order_id`.

```python
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class RazorpayOrderRequest:
    amount: int  # In smallest currency unit (e.g., paise)
    currency: str = "INR"
    receipt: Optional[str] = None
    notes: Dict[str, Any] = field(default_factory=dict)
    partial_payment: bool = False
```

### B. Payment Capture Request
Used if the payment is authorized but needs manual capture.

```python
@dataclass
class RazorpayCaptureRequest:
    amount: int  # In smallest currency unit
    currency: str = "INR"
```

### C. Signature Verification Payload
The data received from the Razorpay frontend checkout to be verified on the backend.

```python
@dataclass
class RazorpayVerificationPayload:
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
```

---

## 2. Project Backend Endpoints (Ready to Test)

The following endpoints are implemented in the `WorkflowViewSet` and are accessible via the tenant domain.

### Authentication & Dashboard (Public Schema)
- `GET /` - Dashboard View
- `POST /login/` - Tenant login
- `POST /logout/` - Session termination

### Payments & Invoices (Tenant Scoped)

#### **1. Invoice Retrieval**
- **Endpoint**: `GET /invoice/<invoice_code>/`
- **Description**: Fetches detailed information about an invoice, its customer, and payment history.
- **Success Response**: `200 OK` with JSON invoice data.

#### **2. Payment Initiation**
- **Endpoint**: `POST /make_payment/`
- **Description**: Initiates a payment record. (Currently uses a stub, but integrated via the `PaymentOrchestrator` in the service layer).
- **Payload**:
  ```json
  {
      "amount": 1000.00,
      "currency": "INR",
      "gateway_name": "rz"
  }
  ```

#### **3. Form Submission (Invoice Creation)**
- **Endpoint**: `POST /submit_form/`
- **Description**: Creates a new customer and invoice based on form data.
- **Payload**:
  ```json
  {
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "9876543210",
      "payable_amount": 1500.00,
      "address": "123 Street, City"
  }
  ```

#### **4. Customer Validations**
- **Endpoint**: `POST /validate_email/`
- **Endpoint**: `POST /validate_phone/`
- **Description**: Triggers validation workflows for customer contact details.

---

## 3. Successful Flow Summary
1. **Identify Invoice**: `GET /invoice/<code:str>/`
2. **Create Order**: `POST /make_payment/` (returns `order_id`)
3. **Frontend**: Open Razorpay Checkout using `order_id`.
4. **Verify**: Call the backend verification logic (to be exposed via a new endpoint or integrated into `make_payment` callback).
