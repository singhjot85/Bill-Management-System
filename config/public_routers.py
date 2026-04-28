from django.conf import settings
from django.urls import path
from rest_framework.routers import DefaultRouter, SimpleRouter

from project_apps.tenants.views import LogoutView, LoginView
from project_apps.utils.admin_utils import public_admin_site

router = SimpleRouter()
if settings.DEBUG:
    router = DefaultRouter()

urlpatterns = [
    path("", view=LoginView.as_view(), name=""),
    path("logout", LogoutView.as_view(), name="logout"),
    path("admin", public_admin_site.urls, name="admin")
]