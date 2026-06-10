from dataclasses import dataclass

from django.db.models import TextChoices


class EventTypeChoices(TextChoices):
    """Event Type Choices, Repersenting template name and event type in general"""

    # Invocing events
    INVOICE_CREATED = "invoice_created", "Invoice Created"

    # Payment Events
    PAYMENT_RECEIVED = "payment_received", "Payment Received"
    PAYMENT_FAILED = "payment_failed", "Payment Failed"
    PAYMENT_REFUNDED = "payment_refunded", "Payment Refunded"


class ChannelTypeChoices(TextChoices):

    SMS = "sms", "SMS"
    EMAIL = "email", "Email"
    WEBHOOK = "webhook", "Webhook"
    PUSH_NOTIFICATION = "push_notification", "Push Notification"


class LangugeTypeChoices(TextChoices):
    ENGLISH = "en", "English"
    HINDI = "hi", "Hindi"
    SPANISH = "es", "Spanish"
    FRENCH = "fr", "French"
    GERMAN = "de", "German"


class LogStatusChoices(TextChoices):
    QUEUED = "queued", "Queued"
    SENT = "sent", "Sent"
    FAILED = "failed", "Failed"
    BOUCED = "bounced", "Bounced"


@dataclass
class NotificationEvent:
    """An notification event is a specific data, required to initiate a notification flow."""

    event_type: "EventTypeChoices"
    recipent_list: list = None
    rendering_context: dict


@dataclass
class ChannelInstruction:
    "Instructions for dispatcher that resolver will generate."

    template_name: "EventTypeChoices"
    channel: "ChannelTypeChoices"
    rendering_context: dict
