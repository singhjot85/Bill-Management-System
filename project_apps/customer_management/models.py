from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings

from project_apps.utils import BetterModelMixin


class CustomerTypeChoices(models.TextChoices):
    """CustomerType Choices"""
    PUBLIC = "public", _("Public Customer")
    PRIVATE = "private", _("Private Customer")
    INTERNAL = "internal", _("Internal User")


class Customer(BetterModelMixin):
    """Customer -> Any user who's using the Business logic."""
    
    name = models.CharField(verbose_name="Customer Name", max_length=255, null=False, blank=False)
    phone = models.CharField(verbose_name="Mobile No", max_length=10)
    email = models.EmailField(null=False, blank=False)
    is_phone_verified = models.BooleanField(verbose_name="Mobile Verified", default=False)
    is_email_verified = models.BooleanField(verbose_name="Email Verified", default=False)
    
    # TODO: This data can have its seperate model
    source = models.TextField(verbose_name="Customer Source", null=True, blank=True)
    customer_type = models.CharField(max_length=124, choices=CustomerTypeChoices.choices)
    external_reference = models.CharField(verbose_name="Customer External Reference", max_length=255, null=True, blank=True)

    details = models.JSONField(verbose_name="Customer Details", default=dict, encoder=DjangoJSONEncoder)


class CustomerAddress(BetterModelMixin):

    customer = models.ForeignKey(to=settings.CUSTOMER_CUSTOMER, on_delete=models.PROTECT, null=False, blank=False, related_name="customer_addresses")

    address_line_1 = models.CharField(max_length=255, null=False, blank=False)
    address_line_2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=125, null=True, blank=True)
    postal_code = models.IntegerField(null=True, blank=True)

    is_primary = models.BooleanField(default=True)
