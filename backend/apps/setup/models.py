from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.core.serializers.json import DjangoJSONEncoder
from django.db import connection, models

from apps.setup.constants import ConfigurationInterfaceChoices
from utils.model_utils import VersionedBetterModelMixin


class Configurations(VersionedBetterModelMixin):

    @staticmethod
    def _get_cache_key(interface_type: str, schema_name: str = None):
        if not schema_name:
            schema_name = connection.schema_name

        return f"{schema_name}:{interface_type}"

    interface_type = models.CharField(max_length=255, choices=ConfigurationInterfaceChoices.choices)
    details = models.JSONField(verbose_name="Content", default=dict, encoder=DjangoJSONEncoder)

    @property
    def cache_key(self):
        return self._get_cache_key(self.interface_type, connection.schema_name)

    @classmethod
    def get_latest_config(self, interface_type: str) -> "Configurations":
        """Getter to get latest config based on versioning
        Args:
            interface_type (str): Interface for the config to get
        Returns:
            config (Configurations): Configurations object for given interface.
        """
        config = None

        if config := cache.get(self.cache_key):
            return config

        try:
            config = self.objects.get(interface_type=interface_type).order_by(self.DEFAULT_ORDERING).first()
        except Exception as e:
            raise ImproperlyConfigured(str(e)) from e

        if config:
            cache.set(self.cache_key, config)

        return config
