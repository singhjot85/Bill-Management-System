from django.contrib.auth import get_user_model
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

from apps.customer_management.models import Customer
from apps.notifications.constants import (
    ChannelTypeChoices,
    EventTypeChoices,
    LangugeTypeChoices,
    LogStatusChoices,
    NotificationTemplateChoices,
)
from utils.model_utils import (
    BetterModelMixin,
    VersionedBetterModelMixin,
    VersionedSafeModelMixin,
)

User = get_user_model()


class NotificationTemplate(VersionedBetterModelMixin):
    """Template model for notifications, Generic model to store a Email or a Message template."""

    # Template Metadata
    template_name = models.CharField(
        max_length=255, choices=NotificationTemplateChoices.choices, null=False, blank=False
    )
    event_type = models.CharField(max_length=124, choices=EventTypeChoices.choices, null=False, blank=False)
    channel = models.CharField(max_length=124, choices=ChannelTypeChoices.choices, null=False, blank=False)
    language = models.CharField(max_length=10, choices=LangugeTypeChoices.choices, null=True, blank=True)

    # Template Content
    subject = models.TextField(null=True, blank=True)
    plain_text = models.TextField(null=True, blank=True)
    html = models.TextField(null=True, blank=True)


class NotificationLog(VersionedSafeModelMixin):
    """Tracks the history and status of all sent notifications.
    The log is used in two places: During Event creation(at dipatcher),
    and during actual implementation flow(during network IO).
    """

    # Event Log
    status = models.CharField(max_length=124, choices=LogStatusChoices.choices, null=False, blank=False)
    task_id = models.CharField(max_length=124, null=True, blank=True)
    channel = models.CharField(max_length=124, choices=ChannelTypeChoices.choices, null=False, blank=False)

    # Startegy Log
    template = models.ForeignKey(
        to=NotificationTemplate,
        on_delete=models.SET_NULL,
        related_name="notification_logs",
        null=True,
        blank=True,
        default=None,
    )
    template_snapshot = models.TextField(null=True, blank=True)
    context_data = models.JSONField(default=dict, encoder=DjangoJSONEncoder)
    errors = models.TextField(null=True, blank=True)


class NotificationPreferences(BetterModelMixin):
    """Store user level prefernce's for notifications."""

    user = models.ForeignKey(
        to=User, on_delete=models.PROTECT, related_name="notification_preferences", null=False, blank=False
    )
    customer = models.ForeignKey(
        to=Customer, on_delete=models.PROTECT, related_name="notification_preferences", null=False, blank=False
    )
    event_type = models.CharField(max_length=124, choices=EventTypeChoices.choices, null=False, blank=False)

    preference_type = models.CharField(max_length=124, choices=ChannelTypeChoices.choices, null=True, blank=True)
    opted_in = models.BooleanField(default=False)
