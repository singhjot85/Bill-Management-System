from django.db import models
from django.core.serializers.json import DjangoJSONEncoder

from project_apps.utils.model_utils import VersionedBetterModelMixin
from project_apps.setup.constants import ConfigurationInterfaceChoices


class Configurations(VersionedBetterModelMixin):

    interface_type = models.CharField(max_length=255, choices=ConfigurationInterfaceChoices.choices)
    details = models.JSONField(verbose_name="Content", default=dict, encoder=DjangoJSONEncoder)