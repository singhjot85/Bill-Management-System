from datetime import date

from rest_framework import serializers

from bma.requests.models import Bill
from bma.utils import generate_random_uuid


class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = "__all__"


class PublicBillSerializer(serializers.Serializer):
    invoice_number = serializers.UUIDField(default=generate_random_uuid)
    organization_name = serializers.CharField()
    organization_address = serializers.CharField()
    name = serializers.CharField()
    email = serializers.EmailField()
    country_code = serializers.CharField()
    phone_number = serializers.CharField()
    invoice_date = serializers.DateField()
    today = serializers.DateField(default=date.today)
    currency = serializers.CharField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    total = serializers.DecimalField(max_digits=12, decimal_places=2)
    org_email = serializers.EmailField()
    org_country_code = serializers.CharField()
    org_phone_number = serializers.CharField()
