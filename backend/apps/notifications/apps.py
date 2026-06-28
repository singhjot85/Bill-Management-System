from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    from django.conf import settings

    default_auto_field = "django.db.models.BigAutoField"
    name = settings.APP_NOTIFICATIONS
