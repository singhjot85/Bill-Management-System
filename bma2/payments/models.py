from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

from bma.constants import (
    CardlessEMIProviderChoices,
    CardNetworkChoices,
    CurrencyChoices,
    OrderInterfaceChoices,
    OrderStateChoices,
    PaymentModeChoices,
    PaymentStateChoices,
)
from bma.core.models import BaseModel
from bma.utils import generate_random_uuid


class Order(BaseModel):

    order_state = models.CharField(
        verbose_name="State of order",
        default=OrderStateChoices.CREATED,
        choices=OrderStateChoices,
        null=False,
        blank=False,
        editable=False,
    )
    currency = models.CharField(
        verbose_name="Currency",
        default=CurrencyChoices.INR,
        choices=CurrencyChoices,
        null=False,
        blank=False,
    )
    amount = models.DecimalField(verbose_name="Order Amount", decimal_places=2, max_digits=13)
    description = models.CharField(verbose_name="Order Description", blank=True, null=True)

    exteranal_order_id = models.CharField(verbose_name="External Order id", null=True, blank=True, editable=False)
    external_reciept_number = models.UUIDField(
        default=generate_random_uuid,
        editable=False,
        primary_key=False,
        unique=True,
        blank=True,
        null=True,
    )
    responses = models.JSONField(
        verbose_name="Order API responses",
        blank=True,
        default=dict,
        encoder=DjangoJSONEncoder,
    )
    details = models.JSONField(blank=True, default=dict, encoder=DjangoJSONEncoder)


class Payment(BaseModel):

    payment_state = models.CharField(
        verbose_name="State of payment",
        default=PaymentStateChoices.CREATED,
        choices=PaymentStateChoices,
        null=False,
        blank=False,
        editable=False,
    )
    requested_by = models.ForeignKey(
        verbose_name="Requested by",
        to="core.Customer",
        on_delete=models.CASCADE,
        default=None,
        null=True,
        blank=True,
        related_name="payments",
    )
    order = models.ForeignKey(
        verbose_name="Order",
        to="payments.Order",
        on_delete=models.CASCADE,
        null=False,
        related_name="payments",
    )

    payment_mode = models.CharField(
        verbose_name="Mode of payment",
        default=PaymentModeChoices.UPI,
        choices=PaymentModeChoices,
    )

    content_type = models.ForeignKey(
        verbose_name="Content Type",
        to="contenttypes.ContentType",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="paymentmodes",
    )
    object_id = models.UUIDField(verbose_name="Object Id")
    payment_object = GenericForeignKey("content_type", "object_id")

    external_payment_id = models.CharField(
        verbose_name="External Payment Id",
        null=True,
        blank=True,
        editable=False,
        max_length=15,
    )
    details = models.JSONField(
        verbose_name="Details of Payment",
        blank=True,
        default=dict,
        encoder=DjangoJSONEncoder,
    )

    # TODO: partial payments mechanism
    is_partial_payment = models.BooleanField(verbose_name="Is Partial Payment", null=True, blank=True)


class OrderInterfaces(BaseModel):
    is_valid = models.BooleanField(null=False, blank=False, default=True)
    interface_type = models.CharField(
        verbose_name="Inteface Type",
        choices=OrderInterfaceChoices,
        null=False,
        blank=False,
    )
    details = models.JSONField(verbose_name="Request Details", default=dict, encoder=DjangoJSONEncoder)

    order = models.ForeignKey(
        verbose_name="Order",
        to="payments.Order",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )

    def save(self, *args, **kwargs):
        (
            OrderInterfaces.objects.filter(interface_type=self.interface_type, order=self.order)
            .exclude(pk=self.pk)
            .update(is_valid=False)
        )  # Invalidate all prev interfaces
        super().save(*args, **kwargs)


class CardDetails(BaseModel):
    card_network = models.CharField(verbose_name="Card Network", choices=CardNetworkChoices)

    number = models.CharField(verbose_name="Card Number", null=False, blank=False)
    name = models.CharField(verbose_name="Card User Name", null=False, blank=False)

    expiry_month = models.CharField(verbose_name="Expiry Month", editable=False)
    expiry_year = models.CharField(verbose_name="Expiry Month", editable=False)
    cvv = models.IntegerField(verbose_name="CVV/CVC")


class InternetBankingDetails(BaseModel):
    bank = models.CharField(verbose_name="Internet Banking Provider", null=False, blank=False)
    details = models.JSONField(verbose_name="Internet Banking Details", default=dict, encoder=DjangoJSONEncoder)


class EMIDetails(BaseModel):
    emi_duration = models.IntegerField(verbose_name="EMI duration", null=False, blank=False)
    card = models.ForeignKey(
        verbose_name="EMI card",
        to="payments.CardDetails",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="emidetails",
    )


class CardlessEMIDetails(BaseModel):
    bank = models.CharField(
        verbose_name="Cardless EMI Provider",
        null=False,
        blank=False,
        choices=CardlessEMIProviderChoices,
    )
    details = models.JSONField(verbose_name="Internet Banking Details", default=dict, encoder=DjangoJSONEncoder)


class WalletDetails(BaseModel):
    bank = models.CharField(verbose_name="Wallet Provider", null=False, blank=False)
    details = models.JSONField(verbose_name="Wallet Details", default=dict, encoder=DjangoJSONEncoder)


class PayLaterDetails(BaseModel):
    provider = models.CharField(verbose_name="Pay Later Provider", null=False, blank=False)
    details = models.JSONField(verbose_name="Pay Later Details", default=dict, encoder=DjangoJSONEncoder)


class UPIDetails(BaseModel):
    upi_provider = models.CharField(verbose_name="UPI service provider")
