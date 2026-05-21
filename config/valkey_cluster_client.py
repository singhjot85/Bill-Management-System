"""Custom valkey cluster client to fix issues with set_many
Curently it doesn't support timeout which is required by django-constance
TODO: Later on we'll adopt django-constaces for feature falgging, do indepth analysis then.
"""
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django_valkey.base_client import _main_exceptions
from django_valkey.cluster_cache.client.default import DefaultClusterClient
from django_valkey.exceptions import ConnectionInterrupted

class PatchedClusterClient(DefaultClusterClient):
    def set_many(self, data, timeout = DEFAULT_TIMEOUT, version = None, client = None):
        client = self._get_client(write=True, client=client)
        pipeline = client.pipeline()
        for key, value in data.items():
            self.set(key, value, timeout, version=version, client=pipeline)
        try:
            pipeline.execute()
        except _main_exceptions as e:
            raise ConnectionInterrupted(connection=client) from e