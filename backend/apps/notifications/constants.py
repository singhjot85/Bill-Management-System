from enum import Enum

from django.db.models import TextChoices


class NotificationTemplateChoices(TextChoices):

    # Good example of when one event can have multiple template's
    WELCOME_NEW_USER = "welcome_new_user", "Welcome New User"
    WELCOME_USER = "welcome_old_user", "Welcome Old User"

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


class EventTypeChoices(TextChoices):
    """Event Type Choices, Repersenting template name and event type in general"""

    WELCOME_USER = "welcome_user", "Welcome User"

    # Invocing events
    INVOICE_CREATED = "invoice_created", "Invoice Created"

    # Payment Events
    PAYMENT_RECEIVED = "payment_received", "Payment Received"
    PAYMENT_FAILED = "payment_failed", "Payment Failed"
    PAYMENT_REFUNDED = "payment_refunded", "Payment Refunded"


class EventPreferences(Enum):
    """Preferences for event, i.e. what all channels that event allows
    Args:
        event_name:  name of the event.
        preferences: list of channels allowed by event.
    """

    WELCOME_USER = EventTypeChoices.WELCOME_USER.value, [ChannelTypeChoices.EMAIL.value]

    INVOICE_CREATED = EventTypeChoices.INVOICE_CREATED.value, [
        ChannelTypeChoices.EMAIL.value,
        ChannelTypeChoices.SMS.value,
    ]

    PAYMENT_RECEIVED = EventTypeChoices.PAYMENT_RECEIVED.value, [ChannelTypeChoices.EMAIL.value]
    PAYMENT_FAILED = EventTypeChoices.PAYMENT_FAILED.value, [ChannelTypeChoices.EMAIL.value]
    PAYMENT_REFUNDED = EventTypeChoices.PAYMENT_REFUNDED.value, [ChannelTypeChoices.EMAIL.value]

    def get_preferences(self) -> set:
        return {*self.value[1]}


class LangugeTypeChoices(TextChoices):
    ENGLISH = "en", "English"
    HINDI = "hi", "Hindi"
    SPANISH = "es", "Spanish"
    FRENCH = "fr", "French"
    GERMAN = "de", "German"


class LogStatusChoices(TextChoices):
    QUEUED = "queued", "Queued"
    IN_PROGRESS = "in_progres", "In Progress"
    SENT = "sent", "Sent"
    FAILED = "failed", "Failed"
    BOUCED = "bounced", "Bounced"
