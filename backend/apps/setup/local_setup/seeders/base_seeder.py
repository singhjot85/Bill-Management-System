import json
import logging
import os
import typing
from abc import ABC, abstractmethod
from typing import Any

from django.conf import settings
from django.core.exceptions import FieldDoesNotExist
from django.db import transaction
from django.db.models import Field, Model
from django_tenants.utils import schema_context

LOGGER = logging.getLogger()


class SeederException(Exception):
    pass


class BaseSeeder(ABC):
    """Base Seeder Templae to be used by each seeder."""

    label: str = ""
    DATA_FILES_PATH = "setup/local_setup/data"
    REGISTERY_KEY = ""

    @staticmethod
    def correct_file_path(file_path: str):
        """Correct the file path, relative to base, root directory

        Args:
            file_path (str): File path

        Returns:
            corrected file path

        Raises:
            SeederException
        """
        if os.path.exists(file_path):
            return file_path

        app_path = os.path.join(settings.APP_DIR, file_path)
        if os.path.exists(app_path):
            return app_path

        root_path = os.path.join(settings.BASE_DIR, file_path)
        if os.path.exists(root_path):
            return root_path

        raise SeederException(f"File not found paths tried: \n\t{file_path}, \n\t{app_path}, \n\t{root_path}")

    @staticmethod
    def file_type_from_path(file_path: str):
        """Return file type from file's extension,

        Args:
            file_path (str): File path

        Returns:
            file extension, txt if no extension
        """
        if (split := file_path.split(".")) > 0:
            return split[-1]

        return "txt"

    @staticmethod
    def load_from_file(path: str, file_type: str = "txt"):
        """Load Data from a file
        Args:
            path (str): Complete file path.
            type (str): Type of data to load.
                txt | json

        Raises:
            SeederException
        """
        if not path:
            raise SeederException("`path` is required to load a file.")

        if not os.path.exists():
            raise SeederException(f"File not found at {path}")

        if file_type not in ["txt", "json"]:
            raise SeederException(f"Invalid file type {file_type}")

        data = None
        with open(file=path, mode="r+", encoding="utf-8") as f:
            if file_type == "txt":
                data = f.read()
            elif file_type == "json":
                data = json.load(f)

        return data

    def __init__(self, file_name: str, **kwargs):
        super().__init__()

        if not hasattr(self, "REGISTERY_KEY"):
            raise SeederException("Register the seeder before using it.")

        if not hasattr(self, "label"):
            raise SeederException("Seeder must have a label attribute")

        self._data_file_name = file_name
        if file_name and hasattr(self, "data_cache_key"):
            cache_key = getattr(self, "data_cache_key")
            self.load_data(file_name, cache_key)

    @property
    def seed_data(self) -> typing.Optional[dict]:

        cache_key = None
        if hasattr(self, "data_cache_key"):
            cache_key = getattr(self, "data_cache_key")
        else:
            LOGGER.warning(f"Seeder: {self.label}, doesn't cache loaded data, not ideal.")

        if hasattr(self, cache_key):
            return getattr(self, cache_key)

        if hasattr(self, "_data_file_name"):
            return self.load_data(self._data_file_name, cache_key)

        return None

    def load_file(self, file_path: str, file_type: str = "txt"):
        """Simple file loading function

        Args:
            file_path (str): Complete/Relative(app-base) path.
            resolved_fields (str, optional): file-type to be fetched,
                default txt, but file extension takes preference.
        """
        file_path = BaseSeeder.correct_file_path(file_path)
        file_type = BaseSeeder.file_type_from_path(file_path)
        content = BaseSeeder.load_from_file(file_path, file_type)

        return content

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

        if hasattr(self, cache_key_name) and getattr(self, cache_key_name):
            return getattr(self, cache_key_name)

        file_path = os.path.join(settings.APP_DIR, self.DATA_FILES_PATH, file_name)
        data = self.load_file(file_path)

        if cache_key_name:
            setattr(self, cache_key_name, data)

        return data

    @abstractmethod
    def seed(self, *args, **kwargs):
        """Abstract seed functionality, that houses the seeding logic, to be overriden for specific seeder."""
        pass

    def run_in_schema(self) -> str:
        """Specify the tenant in which the seeder should run

        Override for seeder specific tenant switching.
        """

        return "public"

    def run(self, *args, **kwargs):
        """Main caller for each seeder, stays in base, rarely overriden"""
        LOGGER.info("[%s] Running Seeder...", self.label)

        try:
            schema_name = self.run_in_schema()
            with schema_context(schema_name):
                with transaction.atomic():  # Atomicity
                    # Idempotency, inside the seed (to be taken care of always).
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

    def load_file_fields(self, val: str, field: str, resolved_fields: dict):
        """
        Load field data from file, big chunks of data like configuation.details, template.html
        is stored in seperate fixture file(s), and fetched using this method during seeding

        Args:
            val (str): Value of file_field, most probably the file path.
            field (str): Name of the field.
            resolved_fields (dict): field_map for resolved fields.
        """
        content = self.load_file()
        resolved_fields[field] = content

    def get_unique_fields(self, model_name: str) -> list:
        """Get unique keys for the model,
        We provide freedom to define unique keys that can be set in data so that object creation remains idempotent
        These are generally fields that are not unique on database level.

        Args:
            model_name (str): Model for which unique fields are to be fetched.

        Returns:
            list of unique fields to fetch model instance.
        """
        unique_keys = self.seed_data.get(f"{model_name}_UNIQUE_KEYS")

        if not unique_keys and hasattr(self, f"{model_name}_UNIQUE_KEYS"):
            unique_keys = getattr(self, f"{model_name}_UNIQUE_KEYS")

        if not unique_keys:
            LOGGER.warning(f"Unique keys not define for model: {model_name}, not ideal.")
        elif not isinstance(unique_keys, (list, tuple)):
            raise SeederException(
                f"Invalid unique keys attribute: {f"{model_name}_UNIQUE_KEYS"} type: {type(unique_keys)}"
            )

        return unique_keys

    def classify_fields(self, model_name: typing.Union[str, Any], filtered_fields: str) -> tuple[dict, dict]:
        """Classify into defaults and uniques"""
        if not isinstance(model_name, str):
            model_name = model_name.__name__

        unique_keys = self.get_unique_fields(model_name)
        uniques = {k: v for k, v in filtered_fields.items() if k in unique_keys}
        defaults = {k: v for k, v in filtered_fields.items() if k not in unique_keys}

        return uniques, defaults
