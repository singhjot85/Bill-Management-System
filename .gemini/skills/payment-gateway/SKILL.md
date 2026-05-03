---
name: payment-gateway
description: Integrate and debug payment gateways. Use when user asks to "set up payments", "test webhook", "verify payment", or "add a gateway".
---

# Payment Gateway Integration

When active:
1. Identify gateway (Razorpay/Stripe)
2. Verify credentials in environment variables
3. Use `scripts/payment_webhook_handler.py` as reference
4. Always verify HMAC signatures, never log raw signatures
5. Use idempotency keys for retries
