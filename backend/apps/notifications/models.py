from django.db import models
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth import get_user_model

from apps.notifications.constants import EventTypeChoices, ChannelTypeChoices, LangugeTypeChoices, LogStatusChoices
from utils.model_utils import VersionedSafeModelMixin, VersionedBetterModelMixin, BetterModelMixin

User = get_user_model()

class NotificationTemplate(VersionedBetterModelMixin):
    """Template model for notifications, Generic model to store a Email or a Message template."""

    # Do we need a template_name, event_type is alreay present ??
    event_type = models.CharField(max_length=124, choices=EventTypeChoices.choices, null=False, blank=False)
    channel = models.CharField(max_length=124, choices=ChannelTypeChoices.choices, null=False, blank=False)
    language = models.CharField(max_length=10, choices=LangugeTypeChoices.choices, null=True, blank=True)
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
        default=None
    )
    template_snapshot = models.TextField(null=True, blank=True)
    context_data = models.JSONField(default=dict, encoder=DjangoJSONEncoder)
    errors = models.TextField(null=True, blank=True)


class NotificationPreferences(BetterModelMixin):
    """Store user level prefernce's for notifications."""
     
    user = models.ForeignKey(to=User, on_delete=models.PROTECT, related_name="notification_preferences", null=False, blank=False)
    event_type = models.CharField(max_length=124, choices=EventTypeChoices.choices, null=False, blank=False)
    
    opted_email = models.BooleanField(default=False)
    opted_sms = models.BooleanField(default=False)
    opted_webhook = models.BooleanField(default=False)
    opted_push_notification = models.BooleanField(default=False)