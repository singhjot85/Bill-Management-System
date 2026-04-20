from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.functional import cached_property

from bma.core.models import BaseModel, BaseUserModel
from bma.utils import generate_random_uuid


def upload_file_path():
    return r"media/invoices"


class Bill(BaseModel):

    PAID = "paid"
    UNPAID = "unpaid"
    PAID_IN_CASH = "paid-in-cash"
    PAYMENT_UNDER_PROCESS = "payment-under-process"

    STATE_CHOICES = (
        (PAID, "Paid Bill"),
        (UNPAID, "Unpaid Bill"),
        (PAID_IN_CASH, "Bill Paid in cash"),
        (PAYMENT_UNDER_PROCESS, "Payment under processing"),
    )

    INR = "INR"
    USD = "USD"

    CURRENCY_CHOICES = ((INR, "Indian Rupee"), (USD, "US Dollar"))

    number = models.UUIDField(default=generate_random_uuid, editable=False, primary_key=False, unique=True)

    name = models.CharField("Bill Name", blank=True)
    state = models.CharField("Category", max_length=255, default=UNPAID, choices=STATE_CHOICES)

    customer = models.ForeignKey(
        verbose_name="Bill Payee",
        to=BaseUserModel,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    total_amount = models.DecimalField(verbose_name="Total Bill Amount", decimal_places=2, max_digits=13)
    currency = models.CharField(verbose_name="Currency", default=INR, choices=CURRENCY_CHOICES)
    description = models.TextField(verbose_name="Bill Description", null=True, blank=True)

    is_partial_payment = models.BooleanField(verbose_name="Is the Amount paid partially", default=False)
    # payment = models.ForeignKey(verbose_name="Current Payment", to=BillPayment, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"Bill<{self.id}>"

    class Meta:
        verbose_name = "Bill"
        verbose_name_plural = "Bills"

    @cached_property
    def created_date(self):
        return self.created.date()

    @cached_property
    def modified_date(self):
        return self.modified.date()


class Document(BaseModel):
    name = models.CharField("Document Name", blank=True)
    template_used = models.TextField("Template used to render", null=True, blank=True)
    file = models.FileField("Document", upload_to=upload_file_path, max_length=255)
    details = models.JSONField("Details of Document", default=dict, encoder=DjangoJSONEncoder)

    def __str__(self):
        return f"{self.file.name}"
