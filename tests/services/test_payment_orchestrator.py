import pytest
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from project_apps.payments_management.models import Payment, Invoice, PaymentStatusChoices, InvoiceStatusChoices
from project_apps.customer_management.models import Customer
from project_apps.services.payment_orchestrator import PaymentOrchestrator

User = get_user_model()

@pytest.mark.django_db
class TestPaymentOrchestrator:
    @pytest.fixture
    def orchestrator(self):
        return PaymentOrchestrator()

    @pytest.fixture
    def invoice(self):
        customer = Customer.objects.create(
            name="Test Customer",
            email="test@example.com",
            phone="1234567890"
        )
        return Invoice.objects.create(
            payable_amount=100.0,
            status=InvoiceStatusChoices.CREATED,
            customer=customer
        )

    @patch('project_apps.services.payment_orchestrator.RazorpayService.create_order')
    def test_create_razorpay_order_success(self, mock_create_order, orchestrator, invoice):
        # Setup mock
        mock_create_order.return_value = {"id": "order_mock_123"}

        payment = orchestrator.create_razorpay_order(invoice.id)

        # Verify database record
        assert payment.order_id == "order_mock_123"
        assert payment.amount == 100.0
        assert payment.invoice == invoice
        assert payment.status == PaymentStatusChoices.CREATED
        mock_create_order.assert_called_once()

    @patch('project_apps.services.payment_orchestrator.RazorpayService.verify_payment_signature')
    @patch('project_apps.services.payment_orchestrator.RazorpayService.fetch_payment')
    def test_verify_razorpay_payment_success(self, mock_fetch_payment, mock_verify_signature, orchestrator, invoice):
        # Create a payment record first
        payment = Payment.objects.create(
            invoice=invoice,
            amount=100.0,
            order_id="order_123",
            status=PaymentStatusChoices.CREATED
        )
        
        # Setup mocks
        mock_verify_signature.return_value = True
        mock_fetch_payment.return_value = {"status": "captured", "id": "pay_123"}

        success = orchestrator.verify_razorpay_payment(
            razorpay_order_id="order_123",
            razorpay_payment_id="pay_123",
            razorpay_signature="valid_sig"
        )

        assert success is True
        
        # Refresh from DB
        payment.refresh_from_db()
        invoice.refresh_from_db()

        assert payment.status == PaymentStatusChoices.COMPLETED
        assert payment.is_verified is True
        assert payment.payment_id == "pay_123"
        assert invoice.status == InvoiceStatusChoices.PAID
        assert invoice.amount_paid == 100.0

    @patch('project_apps.services.payment_orchestrator.RazorpayService.verify_payment_signature')
    def test_verify_razorpay_payment_failure(self, mock_verify_signature, orchestrator, invoice):
        payment = Payment.objects.create(
            invoice=invoice,
            amount=100.0,
            order_id="order_failed",
            status=PaymentStatusChoices.CREATED
        )
        
        mock_verify_signature.return_value = False

        success = orchestrator.verify_razorpay_payment(
            razorpay_order_id="order_failed",
            razorpay_payment_id="pay_failed",
            razorpay_signature="invalid_sig"
        )

        assert success is False
        payment.refresh_from_db()
        assert payment.status == PaymentStatusChoices.FAILED
        assert payment.is_verified is False
