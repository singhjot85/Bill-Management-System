from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

from project_apps.setup.constants import ConfigurationInterfaceChoices
from project_apps.utils.model_utils import VersionedBetterModelMixin


class Configurations(VersionedBetterModelMixin):

    interface_type = models.CharField(max_length=255, choices=ConfigurationInterfaceChoices.choices)
    details = models.JSONField(verbose_name="Content", default=dict, encoder=DjangoJSONEncoder)
