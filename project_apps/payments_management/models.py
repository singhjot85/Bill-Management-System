import random
from datetime import datetime

from django.db import models, connection
from django.utils.translation import gettext_lazy as _
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings

from project_apps.utils import BetterModelMixin

# TODO: Move to a util, and do some refining.
def get_invoice_url(obj):
    if settings.DEBUG:
        return r"local_testing/"

    if isinstance(obj, Invoice):
        pass

class InvoiceStatusChoices(models.TextChoices):
    """Invoice Status Choices"""

    CREATED = "created", _("Created")
    PAID = "paid", _("Paid")
    DEFAULTED = "defaulted", _("defaulted")
    INVALID = "invalid", _("Invalid")


class Invoice(BetterModelMixin):
    RAND_INT_RANGE = (0, 10000)

    invoice_date = models.DateField(verbose_name="Invoices on", null=True, blank=True)
    due_date = models.DateField(verbose_name="Due Date", null=True, blank=True)
    status = models.CharField(max_length=125, choices=InvoiceStatusChoices.choices)
    invoice_number = models.CharField(max_length=255, null=True, blank=True)
    document = models.FileField(upload_to=get_invoice_url, null=True, blank=True)
    context_data = models.JSONField(default=dict, encoder=DjangoJSONEncoder)
    payable_amount = models.FloatField(null=True, blank=True)
    amount_paid = models.FloatField(null=True, blank=True)

    generated_by = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name="invoices")
    customer = models.ForeignKey(to=settings.CUSTOMER_CUSTOMER, on_delete=models.PROTECT, null=True, blank=True, related_name="invoices")
    template = models.ForeignKey(to=settings.PAYMENT_INVOICETEMPLATE, on_delete=models.PROTECT, null=True, blank=True, related_name="invoices")

    def _generate_invoice_number(self):
        """
        TODO: Very weak logic, refine it
        """
        from project_apps.tenants.models import OrganizationTenant
        org = OrganizationTenant.models.get(schema_name=connection.schema_name)
        return {org.name}-{random.randint(*self.RAND_INT_RANGE)}

    def __str__(self):
        return self.invoice_number
    
    def save(self, *args, **kwargs):
        self.invoice_number = self._generate_invoice_number()
        return super().save(*args, **kwargs)


class PaymentStatusChoices(models.TextChoices):

    CREATED = "created", _("Created")
    PROCESSING = "processing", ("In Progress")
    COMPLETED = "completed", _("Completed")
    FAILED = "failed", _("Failed")

class PaymentGatewayChoices(models.TextChoices):
    
    PAYPAL = "pp", _("Pay Pal")
    RAZORPAY = "rz", _("Razorpay")


class Payment(BetterModelMixin):
    """
    TODO: This model will require more refining
    """

    INR = "INR"
    USD = "USD"

    CURRENCY_CHOICES = ((INR, "Indian Rupee"), (USD, "US Dollar"))

    status = models.CharField(max_length=124, choices=PaymentStatusChoices.choices)
    payment_type = models.CharField(max_length=255, null=True, blank=True)
    order_id = models.CharField(max_length=255, null=True, blank=True)
    payment_id = models.CharField(max_length=255, null=True, blank=True)
    amount = models.FloatField()
    currency = models.CharField(max_length=124, choices=CURRENCY_CHOICES, null=True, blank=True)

    raw_payment_response = models.JSONField(default=dict, encoder=DjangoJSONEncoder)
    gateway_name = models.CharField(verbose_name="Paymeny Gateway", max_length=124, choices=PaymentGatewayChoices.choices)
    gateway_signature = models.CharField(max_length=255, null=True, blank=True)

    is_verified = models.BooleanField(default=False)
    verified_on = models.DateTimeField()

    payee = models.ForeignKey(to=settings.CUSTOMER_CUSTOMER, on_delete=models.PROTECT, null=True, blank=True, related_name="payments")
    verified_by = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name="payments")
    invoice = models.ForeignKey(to=settings.PAYMENT_INVOICE, on_delete=models.PROTECT, null=True, blank=True, related_name="payments")

    def _mark_payment_verified(self, *args, **kwargs):
        self.is_verified = True
        self.verified_on = datetime.now()
        super().save(update_fields=["is_verified", "verified_on"], *args, **kwargs)