import json
import logging
import os
from abc import ABC, abstractmethod
from typing import Any

from django.conf import settings
from django.db import transaction
from django.db.models import Field, FieldDoesNotExist, Model

LOGGER = logging.getLogger()


class SeederException(Exception):
    pass


class BaseSeeder(ABC):
    """Base Seeder Templae to be used by each seeder."""

    label: str = ""
    DATA_FILES_PATH = "project_apps/setup/local_setup/data"

    @abstractmethod
    def seed(self, *args, **kwargs):
        """Abstract seed functionality, that houses the seeding logic, to be overriden for specific seeder."""
        pass

    def run(self, *args, **kwargs):
        """Main caller for each seeder, stays in base, DO NOT override this."""
        LOGGER.info("[%s] Running Seeder...", self.label)

        try:
            # Indempotent seeding, each seed should succeed fully only.
            with transaction.atomic():
                self.seed(args, kwargs)

        except Exception as e:
            LOGGER.error("[%s] Seeder run failed.", self.label)
            raise SeederException(str(e)) from e

        LOGGER.info("[%s] Seeder ran successfully.", self.label)

    @staticmethod
    def filter_model_fields(model: type[Model], fields: dict[str, Any], only_concrete: bool = True) -> dict[str, Any]:
        """Filter Model fields from given fields, cleaner for raw field names.

        Args:
            model: Model Class.
            fields: Mapping for field and value.
            only_concrete: Filter only Concrete fields.
                i.e., Skip (relationships, virtual fields, etc.)
                Defaults to True.

        Returns:
            filtered: Filtered Fields.

        Examples:
            >>> filter_model_fields(User, {'name': 'John', 'invalid': 'x'})
            {'name': 'John'}
        """
        filtered = {}
        for key, value in fields.items():
            try:
                field: Field = model._meta.get_field(key)
                if only_concrete and not field.concrete:
                    continue
                filtered[key] = value

            except FieldDoesNotExist:
                if only_concrete:
                    # Silently skip non-existent fields in strict mode
                    LOGGER.debug("Field [%s] doesn't exist on model [%s], skipping", key, model.__name__)
                else:
                    # Include if it's a model attribute (property, method, etc.)
                    if hasattr(model, key):
                        LOGGER.debug("Including non-field attribute [%s] for model [%s]", key, model.__name__)
                        filtered[key] = value
                    else:
                        LOGGER.warning("Attribute [%s] doesn't exist on model [%s]", key, model.__name__)

        return filtered

    def load_data(self, file_name: str, cache_key_name: str = None):
        """Load data from a file and keep in object cache for reuse.
        Args:
            file_name (str): Name of the file to load from.
            cache_key_name (str, optional): key name for object cache.
        Returns:
            Loaded data
        """
        if len(file_name.split(".")) < 2:
            raise SeederException(f"Invalid file name [{file_name}] include file extension also.")

        if hasattr(self, cache_key_name):
            return getattr(self, cache_key_name)

        file_path = os.path.join(settings.BASE_DIR, self.DATA_FILES_PATH, file_name)

        data = None
        if file_name.split(".")[-1] == "json":
            with open(file_path) as f:
                data = json.load(f)
        else:
            with open(file_path) as f:
                data = f.read()

        if cache_key_name:
            setattr(self, cache_key_name, data)

        return data
