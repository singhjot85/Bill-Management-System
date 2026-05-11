import json

from django.views.generic import TemplateView
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login, logout
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from project_apps.tenants.serializers import LoginSerializer, UserSerializer
from project_apps.utils.view_utils import AuthenticatedViewMixin
from project_apps.setup.models import Configurations, ConfigurationInterfaceChoices


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
            request, 
            username=serializer.validated_data["username"], 
            password=serializer.validated_data["password"]
        )
        
        if user:
            login(request, user)
            return Response(UserSerializer(user).data)
        
        return Response(
            {"detail": "Invalid credentials"}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def logout(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        return Response(UserSerializer(request.user).data)


class DashboardView(AuthenticatedViewMixin, TemplateView):
    template_name = "views/dashboard/public_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["data"] = {"org": {"name": "BMA Dashboard"}}
        context["navbar_config"] = (
            Configurations.objects.filter(interface_type=ConfigurationInterfaceChoices.UI_CONFIGURATION.value)
            .order_by(*Configurations.DEFAULT_ORDERING)
            .first().details
        )

        return context


class LoginView(View):
    template_name = "views/auth/login.html"
    redirect_url = "dashboard"

    def get(self, request: HttpRequest, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.redirect_url)

        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect(self.redirect_url)

        return render(request, self.template_name, {"errors": "Invalid username or password"}, status=401)


class LogoutView(TemplateView):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect("login")

class IsAllowed(AuthenticatedViewMixin, View):

    def get(self, request: HttpRequest, *args, **kwargs):
        user = request.user
        permissions = request.GET.get("permissions_to_check")

        data = {}
        for permission in permissions:
            data["permission"] = None
            if hasattr(user, permission):
                data["permission"] = user.permission
            else:
                data["permission"] = user.has_perm(permission)
        
        content = json.dumps(data).encode()
        return HttpResponse(content)
