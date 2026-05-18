from django.db import connection
from django.contrib.auth import authenticate, login, logout
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import MethodNotAllowed

from project_apps.tenants.serializers import LoginSerializer, UserSerializer
from project_apps.tenants.models import 

class AuthViewSet(viewsets.ViewSet):
    """
    API Endpoints for Authentication
    """

    permission_classes = [AllowAny]

    @action(detail=False, methods=["post"])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request, username=serializer.validated_data["username"], password=serializer.validated_data["password"]
        )

        if user:
            login(request, user)
            return Response(UserSerializer(user).data)

        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def logout(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        return Response(UserSerializer(request.user).data)


class BrandingViewSet(viewsets.ViewSet):
    
    def create(self, request, *args, **kwargs):
        return MethodNotAllowed("Bradning data not editable, currently!!")
    
    def list(self, request, *args, **kwargs):

        branding = OrganizationBranding.objects.fil

        return Response(data, status=status.HTTP_200_OK)