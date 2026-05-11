# Payment Gateway Interface
Base: create_order(), verify_payment(), process_webhook(), refund_payment()
Implementations: Razorpay, Stripe
Add new: extend PaymentGatewayHandler, register in factory
