from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from project_apps.customer_management.serializers import (
    EmailValidationSerializer,
    FormSubmitSerializer,
    InvoiceLookupSerializer,
    PaymentCreateSerializer,
    PhoneValidationSerializer,
)
from project_apps.payments_management.models import Invoice


def send_validation_email(email):
    return {
        "verification_id": f"email:{email}",
        "delivery_status": "queued_stub",
    }


def send_validation_message(phone):
    return {
        "verification_id": f"phone:{phone}",
        "delivery_status": "queued_stub",
    }


class WorkflowViewSet(ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=["post"], url_path="validate_email")
    def validate_email(self, request):
        serializer = EmailValidationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = send_validation_email(serializer.validated_data["email"])
        return Response(result, status=status.HTTP_202_ACCEPTED)

    @action(detail=False, methods=["post"], url_path="validate_phone")
    def validate_phone(self, request):
        serializer = PhoneValidationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = send_validation_message(serializer.validated_data["phone"])
        return Response(result, status=status.HTTP_202_ACCEPTED)

    @action(detail=False, methods=["post"], url_path="make_payment")
    def make_payment(self, request):
        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save()
        return Response(PaymentCreateSerializer(payment).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="submit_form")
    def submit_form(self, request):
        serializer = FormSubmitSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "can_retry": True,
                    "code": request.data.get("code"),
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        invoice = serializer.save()
        return Response(
            {
                "code": invoice.invoice_number,
                "invoice": InvoiceLookupSerializer(invoice).data,
                "backend_process": invoice.context_data.get("backend_process", {}),
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["get"], url_path=r"invoice/(?P<code>[^/.]+)")
    def invoice(self, request, code=None):
        invoice = (
            Invoice.available_objects.select_related("customer")
            .prefetch_related("payments")
            .filter(invoice_number=code)
            .first()
        )
        if not invoice:
            return Response({"detail": "Invoice not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(InvoiceLookupSerializer(invoice).data)
