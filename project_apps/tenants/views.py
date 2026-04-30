from django.views.generic import TemplateView
from django.http.request import HttpRequest
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login, logout

from project_apps.utils.view_utils import AuthenticatedViewMixin
from project_apps.setup.models import Configurations, ConfigurationInterfaceChoices


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


class TestUI(View):

    def get(self, request: HttpRequest, *args, **kwargs):
        from django.http.response import HttpResponse

        return HttpResponse(y)
