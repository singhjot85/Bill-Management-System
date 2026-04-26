from django.conf import settings
from django.contrib import admin
from django.urls import path
from rest_framework.routers import DefaultRouter, SimpleRouter

from project_apps.tenants.views import LogoutView, LoginView

router = SimpleRouter()
if settings.DEBUG:
    router = DefaultRouter()

urlpatterns = [
    path("", view=LoginView.as_view(), name="login"),
    # path("", LoginView.as_view(), "login"),
    path("/logout", LogoutView.as_view(), name="logout")
]