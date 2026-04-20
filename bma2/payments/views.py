from datetime import date

from django.http.response import HttpResponse
from rest_framework import status as APIStatus
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.request import Request
from rest_framework.response import Response

from bma.core.constants import APIRequestMethods as Method
from bma.core.models import Customer
from bma.payments.client import api_key  # noqa
from bma.payments.models import Order, Payment
from bma.payments.serializers import ExternalOrderSerializer, ExternalPaymentSerializer
from bma.requests.serializers import PublicBillSerializer
from bma.utils import add_rendered_pdf_to_response, get_contenttype_for_payment


class PublicPaymentAPI(viewsets.ViewSet):
    """
    This will be a public endpoint and login won't be required for this
    """

    authentication_classes = []
    permission_classes = []
    template_name = "public_datacapture.html"
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    BILL_TEMPLATE_NAME = "basic_bill.html"

    def list(self, request: Request, *args, **kwargs):
        response = {}

        serializer = ExternalOrderSerializer()
        paymt_serializer = ExternalPaymentSerializer()

        response = {
            "order_serializer": serializer,
            "payment_serializer": paymt_serializer,
        }

        return Response(response, status=APIStatus.HTTP_200_OK)

    def create(self, request: Request, *args, **kwargs):
        order_id = request.data.get("order_id", None)
        customer_id = request.data.get("user_id", None)
        payment_mode = request.data.get("payment_mode", None)

        if not (order_id and customer_id and payment_mode):
            return Response({}, status=APIStatus.HTTP_400_BAD_REQUEST)

        order: Order = Order.objects.get(id=order_id)
        customer: Customer = Customer.objects.get(id=customer_id)

        payment = self._create_payment(order, customer, payment_mode)

        data = {
            "payload": {
                "key": api_key,
                "amount": order.amount,
                "currency": order.currency,
                "name": customer.name,
                "description": order.details,
                "order_id": order.exteranal_order_id,
                "callback_url": "/verify",
            },
            "id": payment.id,
        }

        return Response(data, status=APIStatus.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def create_user(self, request: Request, *args, **kwargs):
        if request.method != Method.POST.value:
            return HttpResponse({}, status=APIStatus.HTTP_400_BAD_REQUEST)

        user, _ = Customer.objects.get_or_create(
            name=request.data.get("name"),
            email=request.data.get("email"),
            country_code=request.data.get("country_code"),
            phone_number=request.data.get("phone_number"),
        )

        return Response(data={"id": str(user.id)}, status=APIStatus.HTTP_201_CREATED)

    @action(detail=False, methods=["post"])
    def create_order(self, request: Request, *args, **kwargs):
        if request.method != Method.POST.value:
            return HttpResponse({}, status=APIStatus.HTTP_400_BAD_REQUEST)

        order, _ = Order.objects.get_or_create(
            currency=request.data.get("currency"),
            amount=request.data.get("amount"),
            description=request.data.get("description"),
        )

        return Response(data={"id": str(order.id)}, status=APIStatus.HTTP_201_CREATED)

    @action(detail=False, methods=["post"])
    def generate_bill(self, request: Request, *args, **kwargs):

        if request.method != Method.POST.value:
            return HttpResponse({}, status=APIStatus.HTTP_400_BAD_REQUEST)

        order_id = request.data.get("order_id", None)
        customer_id = request.data.get("user_id", None)
        payment_id = request.data.get("payment_id", None)

        data = self._get_bill_data(order_id, customer_id, payment_id)

        response: HttpResponse = add_rendered_pdf_to_response(template=self.BILL_TEMPLATE_NAME, data=data)
        return response

    def _get_bill_data(self, order_id, customer_id, payment_id):
        order: Order = Order.objects.get(id=order_id)
        payment: Payment = Payment.objects.get(id=payment_id)  # noqa: F841
        customer: Customer = Customer.objects.get(id=customer_id)

        data = {
            "organization_name": "Org Pvt. Ltd.",
            "organization_address": "38 B, Cawasji Patel Street, Fort, Mumbai",
            "name": customer.name,
            "email": customer.email,
            "country_code": customer.country_code,
            "phone_number": customer.phone_number,
            "invoice_date": date.today(),
            "today": date.today(),
            "currency": order.currency,
            "amount": order.amount,
            "total": order.amount,
            "org_email": "org@mail.com",
            "org_country_code": "+91",
            "org_phone_number": "12345 12345",
        }

        serializer = PublicBillSerializer(data=data)
        if serializer.is_valid():
            return serializer.validated_data
        else:
            return serializer.errors

    def _create_payment(self, order, customer, payment_mode):
        content_type, Model = get_contenttype_for_payment(payment_mode)
        object = Model.objects.create()

        payment, _ = Payment.objects.get_or_create(
            order=order,
            requested_by=customer,
            payment_mode=payment_mode,
            content_type=content_type,
            object_id=str(object.id),
        )
        return payment
