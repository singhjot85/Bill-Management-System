from django.contrib import admin

from apps.notifications.models import (
    NotificationLog,
    NotificationPreferences,
    NotificationTemplate,
)
from utils.admin_utils import private_admin_site


@admin.register(NotificationTemplate, site=private_admin_site)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ("template_name", "event_type", "channel", "version", "is_active", "created")
    list_filter = ("channel", "is_active", "event_type")
    search_fields = ("template_name", "event_type", "subject")
    readonly_fields = ("version_major", "version_minor", "version_patch", "version")


@admin.register(NotificationLog, site=private_admin_site)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ("id", "recipient_user", "event_type", "channel", "status", "sent_at")
    list_filter = ("status", "channel", "event_type")
    search_fields = ("recipient_user__email", "event_type", "task_id")
    readonly_fields = ("id", "created", "modified", "sent_at")


@admin.register(NotificationPreferences, site=private_admin_site)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ("user", "event_type", "opted_email", "opted_sms", "is_active")
    list_filter = ("is_active", "opted_email", "opted_sms")
    search_fields = ("user__email", "event_type")


private_admin_site.register(NotificationPreferences, NotificationPreferenceAdmin)
private_admin_site.register(NotificationLog, NotificationLogAdmin)
private_admin_site.register(NotificationTemplate, NotificationTemplateAdmin)