from django.contrib.auth import get_user_model
from rest_framework import serializers

from project_apps.tenants.models import OrganizationBranding

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


# TODO: Figure out a way for public user registration
# Bigger question is, is that required ???
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]
        read_only_fields = ["id"]


class BrandingSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrganizationBranding
        fields = "__all__"
