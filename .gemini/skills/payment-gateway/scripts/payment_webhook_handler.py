#!/usr/bin/env python
"""Base payment gateway webhook handler"""
import hmac, hashlib
from datetime import datetime
from django.conf import settings
from django.db import transaction
from payments_management.models import Payment

class PaymentGatewayHandler:
    def __init__(self, gateway_name):
        self.gateway_name = gateway_name
        secrets = {"razorpay": settings.RAZORPAY_WEBHOOK_SECRET, "stripe": settings.STRIPE_WEBHOOK_SECRET}
        self.secret = secrets.get(gateway_name, "")

    def verify_signature(self, payload, signature):
        expected = hmac.new(self.secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)

    @transaction.atomic
    def process_payment(self, data):
        try:
            payment = Payment.objects.select_related("invoice").get(
                order_id=data["order_id"], gateway_name=self.gateway_name
            )
        except Payment.DoesNotExist:
            return {"error": "Payment not found"}

        payment.payment_id = data.get("payment_id")
        payment.status = data.get("status", "COMPLETED")
        payment.raw_payment_responses = data
        payment.verified_on = datetime.now()
        payment.verified_flag = True
        payment.save()

        if payment.status == "COMPLETED":
            invoice = payment.invoice
            invoice.amount_paid = payment.amount
            invoice.status = "PAID"
            invoice.save()
        return {"success": True, "payment_id": payment.id}
