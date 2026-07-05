---
title: Payments Management
type: implementation
app: payments_management
last_updated: 2026-06-15
tags: [django, payments, razorpay, invoicing]
---

# Payments Management

## Purpose
The `payments_management` module is a core tenant-scoped application responsible for handling invoices, payment records, and template management.

It encapsulates the logic for financial transactions, integrating with external payment gateways (primarily Razorpay) to ensure secure and audited payment processing.

## Quick Start
Ensure migrations are applied:
```bash
python manage.py migrate
```

## Key Concepts
- **Invoice Lifecycle**: Tracks billing details from creation to `PAID` status.
- **Payment Orchestration**: Coordinates between gateway-specific services and internal database state using `PaymentOrchestrator`.
- **Atomic Transactions**: All status updates involving both `Payment` and `Invoice` records are wrapped in atomic transactions.
- **Race Condition Protection**: Utilizes `select_for_update()` during payment verification.

## API Reference
This app is primarily consumed internally by the `customer_management` app and the frontend via the service layer.

| Service Method | Description |
| :--- | :--- |
| `create_razorpay_order` | Generates a Razorpay order and internal `Payment` record |
| `verify_razorpay_payment` | Verifies gateway signature and updates status atomically |

## Configuration
Requires the following settings in your `.env` or Django settings:
- `RAZORPAY_KEY_ID`: Your Razorpay API Key ID.
- `RAZORPAY_KEY_SECRET`: Your Razorpay API Secret.

## Testing
Run the payment-specific test suite:
```bash
pytest backend/tests/payment_management/
```

## Related Documentation
- [Payments Pattern](../../../docs/patterns/payments.md)
- [Razorpay Integration Spec](../../../docs/integrations/razorpay.md)
- [Invoicing Logic](../../../docs/architecture/data-models.md)
