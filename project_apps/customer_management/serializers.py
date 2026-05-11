from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from project_apps.customer_management.models import Customer, CustomerAddress, CustomerTypeChoices
from project_apps.payments_management.models import Invoice, InvoiceStatusChoices, Payment


class EmailValidationSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PhoneValidationSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=10)


class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "payment_id",
            "payment_type",
            "order_id",
            "amount",
            "currency",
            "gateway_name",
            "status",
            "raw_payment_response",
        ]
        read_only_fields = ["payment_id", "order_id", "status", "raw_payment_response"]

    def create(self, validated_data):
        payment = Payment(
            **validated_data,
            status="processing",
            payment_id=PaymentCreateService.next_payment_id(),
            order_id=PaymentCreateService.next_order_id(),
            raw_payment_response={
                "provider": "stub",
                "message": "Payment gateway integration placeholder.",
            },
        )
        payment.save()
        return payment


class PaymentCreateService:
    @staticmethod
    def next_payment_id():
        return f"PAY-{timezone.now().strftime('%Y%m%d%H%M%S%f')}"

    @staticmethod
    def next_order_id():
        return f"ORD-{timezone.now().strftime('%Y%m%d%H%M%S%f')}"


class FormSubmitSerializer(serializers.Serializer):
    code = serializers.CharField(required=False, allow_blank=True)
    name = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=10)
    payment_method = serializers.CharField(required=False, allow_blank=True)
    payment_id = serializers.CharField(required=False, allow_blank=True)
    payable_amount = serializers.FloatField(required=False, min_value=0)
    email_verification_id = serializers.CharField(required=False, allow_blank=True)
    phone_verification_id = serializers.CharField(required=False, allow_blank=True)

    def validate_code(self, value):
        return value.strip()

    @transaction.atomic
    def create(self, validated_data):
        code = validated_data.get("code")
        if code:
            existing_invoice = Invoice.available_objects.filter(invoice_number=code).first()
            if existing_invoice:
                return existing_invoice

        customer = Customer.objects.create(
            name=validated_data.get("name", ""),
            phone=validated_data["phone"],
            email=validated_data["email"],
            is_phone_verified=bool(validated_data.get("phone_verification_id")),
            is_email_verified=bool(validated_data.get("email_verification_id")),
            customer_type=CustomerTypeChoices.PUBLIC,
            details={
                "payment_method": validated_data.get("payment_method", ""),
                "workflow": "dynamic_form",
            },
        )
        CustomerAddress.objects.create(
            customer=customer,
            address_line_1=validated_data.get("address", ""),
            is_primary=True,
        )

        invoice = Invoice.objects.create(
            invoice_number=code or None,
            invoice_date=timezone.now().date(),
            status=InvoiceStatusChoices.CREATED,
            customer=customer,
            payable_amount=validated_data.get("payable_amount"),
            amount_paid=0,
            context_data={
                "workflow": "dynamic_form",
                "backend_process": {
                    "status": "queued_stub",
                    "queued_at": timezone.now().isoformat(),
                },
            },
        )

        payment_id = validated_data.get("payment_id")
        if payment_id:
            Payment.available_objects.filter(payment_id=payment_id, invoice__isnull=True).update(
                payee=customer,
                invoice=invoice,
                payment_type=validated_data.get("payment_method", ""),
            )

        return invoice


class InvoiceLookupSerializer(serializers.ModelSerializer):
    code = serializers.CharField(source="invoice_number")
    customer = serializers.SerializerMethodField()
    payments = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            "id",
            "code",
            "invoice_date",
            "due_date",
            "status",
            "payable_amount",
            "amount_paid",
            "customer",
            "payments",
            "context_data",
        ]

    def get_customer(self, obj):
        if not obj.customer_id:
            return None
        return {
            "name": obj.customer.name,
            "email": obj.customer.email,
            "phone": obj.customer.phone,
        }

    def get_payments(self, obj):
        return [
            {
                "payment_id": payment.payment_id,
                "status": payment.status,
                "amount": payment.amount,
                "currency": payment.currency,
                "gateway_name": payment.gateway_name,
            }
            for payment in obj.payments.all()
        ]
