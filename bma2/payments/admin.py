from django.contrib import admin, messages
from django.contrib.contenttypes.models import ContentType
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from bma.payments.client import RazorPayClient
from bma.payments.models import (
    CardDetails,
    CardlessEMIDetails,
    EMIDetails,
    InternetBankingDetails,
    Order,
    OrderInterfaces,
    PayLaterDetails,
    Payment,
    WalletDetails,
)


@admin.action(description="Generate orders")
def generate_multiple_order_id(modeladmin, request, queryset):

    if len(queryset) < 1:
        messages.error(request, "ERROR - No objects selcted !!")

    try:
        for obj in queryset:
            client = RazorPayClient(obj)
            response = client.create_order()
            if response["is_success"]:
                messages.success(request, f"Order Created in core for [{obj}]")
    except Exception as exc:
        error_msg = str(exc)
        messages.error(request, f"ERROR occurred generating order {error_msg}")


class PaymentInline(admin.TabularInline):
    """
    Inline payments section within the Order detail page
    """

    model = Payment
    extra = 0
    fields = ("id", "payment_state", "payment_mode", "external_payment_id", "created")
    readonly_fields = (
        "id",
        "payment_state",
        "payment_mode",
        "external_payment_id",
        "created",
    )
    can_delete = False
    show_change_link = True


class OrderInterfacesInline(admin.TabularInline):
    """
    Inline order interfaces section within the Order detail page
    """

    model = OrderInterfaces
    extra = 0
    fields = ("interface_type", "is_valid", "created")
    readonly_fields = ("interface_type", "is_valid", "created")
    can_delete = False
    show_change_link = True


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Detailed admin view for Order model
    """

    list_display = (
        "id",
        "order_state",
        "display_amount",
        "external_reciept_number",
        "exteranal_order_id",
        "created",
        "modified",
    )
    list_filter = (
        "order_state",
        "currency",
        "created",
        "modified",
    )
    search_fields = (
        "id",
        "exteranal_order_id",
        "external_reciept_number",
    )
    readonly_fields = (
        "external_reciept_number",
        "exteranal_order_id",
        "created",
        "modified",
    )
    ordering = ("-created",)
    date_hierarchy = "created"
    inlines = [PaymentInline, OrderInterfacesInline]
    actions = [generate_multiple_order_id]

    # organize the edit form in sections
    fieldsets = (
        (_("Basic Info"), {"fields": ("currency", "amount", "description")}),
        (
            _("External Identifiers"),
            {"fields": ("external_reciept_number", "exteranal_order_id")},
        ),
        (
            _("JSON Data"),
            {"classes": ("collapse",), "fields": ("responses", "details")},
        ),
        (_("Timestamps"), {"fields": ("created", "modified")}),
    )

    def display_amount(self, obj: Order):
        """
        Show amount with currency in list display.
        """
        return format_html("<b>{} {}</b>", obj.currency, obj.amount)

    display_amount.short_description = "Amount"

    def has_delete_permission(self, request, obj: Order = None):
        """
        Optional: Prevent deleting Orders directly from admin.
        """
        return False

    def get_queryset(self, request):
        """
        Prefetch related payments for performance optimization
        """
        qs = super().get_queryset(request)
        return qs.prefetch_related("payments")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Detailed admin for Payment model
    """

    list_display = (
        "id",
        "payment_state",
        "payment_mode",
        "display_order",
        "requested_by",
        "external_payment_id",
        "is_partial_payment",
        "created",
    )
    list_filter = (
        "payment_state",
        "payment_mode",
        "is_partial_payment",
        "created",
    )
    search_fields = (
        "id",
        "external_payment_id",
        "order__id",
        "requested_by__username",
        "requested_by__email",
    )
    readonly_fields = (
        "id",
        "payment_state",
        "payment_object",
        "external_payment_id",
        "created",
        "modified",
    )
    # raw_id_fields = ("order", "requested_by", "content_type")
    date_hierarchy = "created"
    ordering = ("-created",)

    fieldsets = (
        (
            _("Basic Info"),
            {
                "fields": [
                    "id",
                    "payment_mode",
                    "is_partial_payment",
                    "external_payment_id",
                ]
            },
        ),
        (_("Payment Method link"), {"fields": ["content_type", "object_id"]}),
        (_("Foreign Links"), {"fields": ["requested_by", "order"]}),
        (_("Payment Details"), {"classes": ("collapse",), "fields": ["details"]}),
        (_("Timestamps"), {"fields": ["created", "modified"]}),
    )

    def display_order(self, obj):
        """Show clickable link to related Order in admin."""
        if obj.order_id:
            return format_html(
                '<a href="/admin/payments/order/{}/change/">{}</a>',
                obj.order_id,
                obj.order_id,
            )
        return "-"

    display_order.short_description = "Order"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "content_type":
            kwargs["queryset"] = ContentType.objects.filter(
                model__in=(
                    "carddetails",
                    "internetbankingdetails",
                    "emidetails",
                    "walletdetails",
                    "paylaterdetails",
                )
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        """
        Optimize by selecting related objects to avoid N+1 queries.
        """
        qs = super().get_queryset(request)
        return qs.select_related("order", "requested_by", "content_type")


@admin.register(OrderInterfaces)
class OrderInterfacesAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "interface_type",
        "is_valid",
        "order",
        "created",
    )
    list_filter = ("interface_type", "is_valid", "created")
    search_fields = ("id", "order__id")
    raw_id_fields = ("order",)


@admin.register(CardDetails)
class CardDetailsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "card_network",
        "number",
        "name",
        "expiry_month",
        "expiry_year",
        "created",
    )
    list_filter = ("card_network", "created")
    search_fields = ("number", "name")


@admin.register(InternetBankingDetails)
class InternetBankingDetailsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "bank",
        "created",
    )
    search_fields = ("bank",)
    list_filter = ("created",)


@admin.register(EMIDetails)
class EMIDetailsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "emi_duration",
        "card",
        "created",
    )
    raw_id_fields = ("card",)
    list_filter = ("emi_duration", "created")
    search_fields = ("card__number",)


@admin.register(CardlessEMIDetails)
class CardlessEMIDetailsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "bank",
        "created",
    )
    list_filter = ("bank", "created")
    search_fields = ("bank",)


@admin.register(WalletDetails)
class WalletDetailsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "bank",
        "created",
    )
    search_fields = ("bank",)
    list_filter = ("created",)


@admin.register(PayLaterDetails)
class PayLaterDetailsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "provider",
        "created",
    )
    search_fields = ("provider",)
    list_filter = ("created",)
