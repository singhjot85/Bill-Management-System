from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.core.serializers.json import DjangoJSONEncoder
from django.db import connection, models

from apps.setup.constants import ConfigurationInterfaceChoices
from utils.model_utils import BetterModelMixin, VersionedBetterModelMixin


class SeederExecutionLog(BetterModelMixin):
    seeder_name = models.CharField(max_length=255)
    schema_name = models.CharField(max_length=255)
    status = models.CharField(max_length=50)  # SUCCESS, FAILED

    class Meta:
        db_table = "seeder_execution_log"
        unique_together = ("seeder_name", "schema_name")

    def __str__(self):
        return f"{self.seeder_name} on {self.schema_name} ({self.status})"


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

        cache_key = self._get_cache_key(interface_type)
        if config := cache.get(cache_key):
            return config

        try:
            config = self.objects.filter(interface_type=interface_type).order_by(*self.DEFAULT_ORDERING).first()
        except Exception as e:
            raise ImproperlyConfigured(str(e)) from e

        if config:
            cache.set(cache_key, config)

        return config
