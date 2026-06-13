from django.contrib import admin

from apps.notifications.models import (
    NotificationLog,
    NotificationPreferences,
    NotificationTemplate,
)
from utils.admin_utils import ReadOnlyAdmin, private_admin_site


class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ["id", "template_name", "event_type", "channel", "version"]
    list_filter = ["template_name", "event_type", "channel", "language"]
    readonly_fields = ["created", "modified", "id", "version", "is_removed"]

    fieldsets = (
        (
            None,
            {
                "fields": ["is_removed", ("template_name", "version"), ("event_type", "channel")],
            },
        ),
        ("Content", {"fields": ["plain_text", "html"], "classes": ["wide"]}),
        ("TimeStamps", {"fields": ["created", "modified"], "classes": ["collapse"]}),
    )


class NotificationLogAdmin(ReadOnlyAdmin):
    list_display = ["id", "status", "task_id", "channel", "version"]
    list_filter = ["status", "channel"]

    fieldsets = (
        (None, {"fields": [("id", "task_id"), ("status", "channel"), "template"]}),
        ("Runtime Data", {"fields": ["template_snapshot", "context_data", "errors"], "classes": ["wide"]}),
    )


class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "event_type", "is_removed"]
    list_filter = ["event_type", "is_removed", "opted_email", "opted_sms", "opted_webhook", "opted_push_notification"]
    readonly_fields = ["created", "modified", "is_removed"]

    fieldsets = (
        (
            None,
            {
                "fields": [
                    "is_removed",
                    "user",
                    "event_type",
                    ("opted_email", "opted_sms", "opted_webhook", "opted_push_notification"),
                ]
            },
        ),
        ("TimeStamp", {"fields": [("created", "modified")], "classes": ["collapse"]}),
    )


private_admin_site.register(NotificationPreferences, NotificationPreferenceAdmin)
private_admin_site.register(NotificationLog, NotificationLogAdmin)
private_admin_site.register(NotificationTemplate, NotificationTemplateAdmin)
