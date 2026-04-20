from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bma.core"
    verbose_name = "Core App"
    verbose_name_plural = "Core Apps"
