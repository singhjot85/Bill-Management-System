from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.core.exceptions import ImproperlyConfigured

from project_apps.setup.constants import ConfigurationInterfaceChoices
from project_apps.utils.model_utils import VersionedBetterModelMixin


class Configurations(VersionedBetterModelMixin):

    interface_type = models.CharField(max_length=255, choices=ConfigurationInterfaceChoices.choices)
    details = models.JSONField(verbose_name="Content", default=dict, encoder=DjangoJSONEncoder)

    @classmethod
    def get_latest_config(self, interface_type: str) -> "Configurations":
        """Getter to get latest config based on versioning
        TODO: Setup caching on project level, and use cached configs
        Args:
            interface_type (str): Interface for the config to get
        Returns:
            config (Configurations): Configurations object for given interface.
        """
        try:
            config = self.objects.get(interface_type=interface_type).order_by(self.DEFAULT_ORDERING).first()
        except Exception as e:
            raise ImproperlyConfigured(str(e)) from e
        
        return config
