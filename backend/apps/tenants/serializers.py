from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import MethodNotAllowed

from backend.apps.tenants.models import OrganizationBranding

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    superuser_status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "is_active", "superuser_status"]
        read_only_fields = fields

    def get_superuser_status(self, instance: "User"):
        return bool(instance.is_staff and instance.is_superuser)

    def create(self, validated_data):
        raise MethodNotAllowed("Create")

    def update(self, instance, validated_data):
        raise MethodNotAllowed("Update")


class BrandingSerializer(serializers.ModelSerializer):
    organization = serializers.SerializerMethodField()

    class Meta:
        model = OrganizationBranding
        fields = [
            "id",
            "is_removed",
            "version",
            "country",
            "phone",
            "email",
            "navbar_icon",
            "navbar_title",
            "footer_icon",
            "footer_text",
            "footer_extra_text",
            "organization",
        ]

    def get_organization(self, instance: OrganizationBranding):
        return instance.organization.name
