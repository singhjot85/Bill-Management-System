from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class TenantConfigurationInterfaceChoices(TextChoices):
    
    UI_CONFIGURATION = "ui_configuration", _("UI configuration")