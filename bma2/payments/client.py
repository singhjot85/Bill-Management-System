import json

from django.conf import settings
from razorpay import Client as rzpayClient
from rest_framework.renderers import JSONRenderer

from bma.payments.models import Order
from bma.payments.serializers import OrderSerializer
from bma.utils import jq_transform_payload

api_key = settings.RAZORPAY_API_KEY
secrete = settings.RAZORPAY_API_SECRETE
"""
TODO: UPI intent flow(mobile installed upi app - also requires webhook implementation)
https://razorpay.com/docs/payments/payment-gateway/s2s-integration/payment-methods/upi/intent/
currently only UPI Collect Flow is implemented
https://razorpay.com/docs/payments/payment-gateway/s2s-integration/payment-methods/upi/collect/
"""


class RazorPayClient:

    def __init__(self, order: Order):
        self.client: rzpayClient = rzpayClient(auth=(api_key, secrete))
        self.order = order
        if not self.order:
            raise Exception("An order is required to make a request")

    def create_order(self) -> str | None:
        """Creates an order and returns razorpay order_id"""
        jq_path = "bma/setup/jqs/request/create_order.jq"
        serializer = OrderSerializer(self.order)
        cleaned_data = {}
        if serializer.is_valid():
            cleaned_data = json.loads(JSONRenderer.render(serializer.data))

        payload = jq_transform_payload(cleaned_data, jq_path)
        response = self.client.order.create(data=payload)

        self._update_to_responses(response, "create_order")
        if response["id"]:
            rz_id = response["id"]
            self.order.exteranal_order_id = rz_id
            self.order.save(update_fields=["exteranal_order_id"])
            return rz_id
        return None

    def _update_to_responses(self, data: dict, key: str):
        prev_responses = self.order.responses
        prev_responses[key] = data
        self.order.responses = prev_responses
        self.order.save(update_fields=["responses"])
