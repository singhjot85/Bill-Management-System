import logging

from django.db import transaction
from django.utils import timezone

from apps.payments_management.models import (
    Invoice,
    InvoiceStatusChoices,
    Payment,
    PaymentGatewayChoices,
    PaymentStatusChoices,
)

from .razorpay_service import RazorpayService

logger = logging.getLogger(__name__)


class PaymentOrchestrator:
    """
    Orchestration layer for managing payments and invoices.
    Coordinates between the Razorpay service and the application database.
    """

    def __init__(self):
        self.razorpay = RazorpayService()

    def create_razorpay_order(self, invoice_id: str) -> Payment:
        """
        Creates a Razorpay order for a given invoice and records it in our database.
        """
        try:
            # Using UUID if possible, but the model uses BetterModelMixin which handles it.
            invoice = Invoice.objects.get(id=invoice_id)
        except Invoice.DoesNotExist:
            logger.error(f"Invoice {invoice_id} not found.")
            raise

        # 1. Create order in Razorpay
        # Razorpay expects amount in paise (float amount * 100)
        order_data = self.razorpay.create_order(
            amount=invoice.payable_amount,
            currency="INR",
            receipt=invoice.invoice_number,
            notes={
                "invoice_id": str(invoice.id),
                "customer_id": str(invoice.customer_id) if invoice.customer else "N/A",
            },
        )

        # 2. Record payment attempt in our database
        payment = Payment.objects.create(
            invoice=invoice,
            amount=invoice.payable_amount,
            currency="INR",
            order_id=order_data["id"],
            status=PaymentStatusChoices.CREATED,
            gateway_name=PaymentGatewayChoices.RAZORPAY,
            raw_payment_response=order_data,
            payee=invoice.customer,
        )

        return payment

    @transaction.atomic
    def verify_razorpay_payment(
        self, razorpay_order_id: str, razorpay_payment_id: str, razorpay_signature: str, user=None
    ) -> bool:
        """
        Verifies a Razorpay payment and updates the corresponding Payment and Invoice records.
        Uses a database transaction to ensure atomicity.
        """
        # 1. Verify the signature locally
        is_valid = self.razorpay.verify_payment_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature)

        try:
            # Use select_for_update to prevent race conditions during verification
            payment = Payment.objects.select_for_update().get(order_id=razorpay_order_id)
        except Payment.DoesNotExist:
            logger.error(f"Payment with order_id {razorpay_order_id} not found.")
            return False

        if is_valid:
            # 2. Fetch full payment details from Razorpay for auditing/verification
            try:
                payment_details = self.razorpay.fetch_payment(razorpay_payment_id)
            except Exception as e:
                logger.error(f"Failed to fetch payment details from Razorpay: {e}")
                # We can still proceed if signature is valid, but details are preferred.
                payment_details = {"verification_error": str(e)}

            # 3. Update payment record atomically
            payment.payment_id = razorpay_payment_id
            payment.gateway_signature = razorpay_signature
            payment.status = PaymentStatusChoices.COMPLETED
            payment.is_verified = True
            payment.verified_on = timezone.now()
            payment.verified_by = user
            payment.raw_payment_response = payment_details
            payment.save()

            # 4. Update invoice record
            invoice = payment.invoice
            if invoice:
                invoice.status = InvoiceStatusChoices.PAID
                invoice.amount_paid = (invoice.amount_paid or 0) + payment.amount
                invoice.save()

            logger.info(
                f"Payment {razorpay_payment_id} verified successfully for invoice {invoice.invoice_number if invoice else 'N/A'}"
            )
            return True
        else:
            payment.status = PaymentStatusChoices.FAILED
            payment.save()
            logger.warning(f"Payment verification failed for order {razorpay_order_id}")
            return False
