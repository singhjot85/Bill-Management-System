from django.conf import settings
from django.urls import path
from rest_framework.routers import DefaultRouter, SimpleRouter

from project_apps.customer_management.views import WorkflowViewSet
from project_apps.utils.admin_utils import private_admin_site

router = SimpleRouter()
if settings.DEBUG:
    router = DefaultRouter()

workflow_validate_email = WorkflowViewSet.as_view({"post": "validate_email"})
workflow_validate_phone = WorkflowViewSet.as_view({"post": "validate_phone"})
workflow_make_payment = WorkflowViewSet.as_view({"post": "make_payment"})
workflow_submit_form = WorkflowViewSet.as_view({"post": "submit_form"})
workflow_invoice = WorkflowViewSet.as_view({"get": "invoice"})

urlpatterns = [
    path("admin/", private_admin_site.urls, name="admin"),
    path("validate_email/", workflow_validate_email, name="validate-email"),
    path("validate_phone/", workflow_validate_phone, name="validate-phone"),
    path("make_payment/", workflow_make_payment, name="make-payment"),
    path("submit_form/", workflow_submit_form, name="submit-form"),
    path("invoice/<str:code>/", workflow_invoice, name="invoice-detail"),
]
urlpatterns.extend(router.urls)
