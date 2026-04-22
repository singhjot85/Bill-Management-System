from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter

# from bma.payments.views import PublicPaymentAPI

router = SimpleRouter()
if settings.DEBUG:
    router = DefaultRouter()

# router.register(r'bill', BillViewSet, basename='bill')
# router.register(r"public/payments", PublicPaymentAPI, basename="public-payments")

urlpatterns = [
    # path("", include("bma.core.urls")),
    path("admin/", admin.site.urls, name="admin"),
]
urlpatterns.extend(router.urls)
