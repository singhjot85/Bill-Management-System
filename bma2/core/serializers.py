from rest_framework import serializers

from bma.core.models import BaseUserModel, Customer


class BaseUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = BaseUserModel
        fields = ["id", "username", "email", "country_code", "phonenumber"]


class PublicCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            "name",
            "email",
            "country_code",
            "phone_number",
        ]
