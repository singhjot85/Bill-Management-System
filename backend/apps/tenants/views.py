from django.contrib.auth import authenticate, login, logout
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed, NotFound
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from backend.apps.tenants.models import OrganizationBranding
from backend.apps.tenants.serializers import (
    BrandingSerializer,
    LoginSerializer,
    UserSerializer,
)


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


class BrandingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Get branding for current tenant, this is open and don't require auth.
    Allowed Urls:
        GET: api/branding?tenant=public
        GET: api/branding/public
    """
    queryset = OrganizationBranding.objects.select_related("organization").all()
    serializer_class = BrandingSerializer
    
    lookup_field = "organization__schema_name"

    def get_queryset(self):
        qs =  super().get_queryset()
        tenant = self.request.query_params.get('tenant')

        if tenant:
            qs = qs.filter(organization__schema_name=tenant)
            if not qs.exists() and self.action == 'retrieve':
                raise NotFound(f"Branding not found for tenant: {tenant}")

        return qs

    def list(self, request, *args, **kwargs):
        """Handle GET requests with tenant filter"""
        tenant = request.query_params.get('tenant')
        
        if tenant:
            queryset = self.get_queryset()
            if queryset.exists():
                serializer = self.get_serializer(queryset.first())
                return Response([serializer.data])
            raise NotFound(f"Branding not found for tenant: {tenant}")
        
        raise MethodNotAllowed("List all not allowed, please specify tenant")
