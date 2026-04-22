from django.conf import settings
from django.contrib import admin
from django.urls import path
from rest_framework.routers import DefaultRouter, SimpleRouter

router = SimpleRouter()
if settings.DEBUG:
    router = DefaultRouter()

urlpatterns = [
    # path("", include("bma.core.urls")),
    path("admin/", admin.site.urls, name="admin"),
]
urlpatterns.extend(router.urls)
