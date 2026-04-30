from django.conf import settings
from django.urls import path
from rest_framework.routers import DefaultRouter, SimpleRouter

from project_apps.tenants.views import LoginView, LogoutView, DashboardView, TestUI
from project_apps.utils.admin_utils import public_admin_site

router = SimpleRouter()
if settings.DEBUG:
    router = DefaultRouter()

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("admin/", public_admin_site.urls, name="admin"),
    path("test-html/", TestUI.as_view(), name="test")
]
