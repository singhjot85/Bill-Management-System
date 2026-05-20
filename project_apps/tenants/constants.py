from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _

class CountryChoices(TextChoices):

    INDIA = "in", _("India")
    US = "us", _("United States")