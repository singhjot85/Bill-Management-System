import json
import logging
import os
import typing
from abc import ABC
import re
from pathlib import Path

from django.conf import settings

from django.conf import settings
from django.db import models, transaction
from django_tenants.utils import schema_context

from apps.setup.models import SeederExecutionLog
from apps.setup.seeder.exceptions import ObjectCreationException, SeederException
from apps.setup.seeder.sources import FixtureSource
from apps.setup.seeder.sources import DataSource
from utils.registry_utils import UnorderedClassRegistry

LOGGER = logging.getLogger(__name__)

seeder_registry = UnorderedClassRegistry()


class Scope:
    PUBLIC = "public"
    PER_TENANT = "per_tenant"


class ObjectCreationMixin:
    """Helper mixin to create database objects from structured payload dictionaries."""

    _model: models.Model
    _model_data: typing.Union[dict, list]
    _default_database = "default"
    _model_wise_unique_fields = {
        "OrganizationTenant": ["schema_name"],
        "OrganizationDomain": ["domain"],
        "OrganizationBranding": ["organization__schema_name"],
        "Configurations": ["interface_type"],
        "User": ["username", "email"],
        "NotificationTemplate": ["template_name", "event_type", "channel", "language"],
    }

    @property
    def model(self) -> typing.Optional[models.Model]:
        if hasattr(self, "_model"):
            return getattr(self, "_model")
        raise ObjectCreationException("models.Model not defined. Use `set_model` to declare a model to process.")

    def set_model(self, kls: type[models.Model]):
        if not (isinstance(kls, type) and issubclass(kls, models.Model)):
            raise ObjectCreationException("models.Model must be a subclass of `django.db.models.Model`.")
        self._model = kls

    @property
    def model_data(self) -> typing.Union[dict, list]:
        if hasattr(self, "_model_data"):
            return getattr(self, "_model_data")
        raise ObjectCreationException("Model data not defined. Use `set_model_data` first.")

    def set_model_data(self, data: typing.Union[dict, list]):
        self._model_data = data

    def get_unique_fields(self, kls: type[models.Model], data: dict = None) -> dict:
        """Extract matching unique fields from data payload to prevent duplicate creations."""
        field_names = data.get(f"{kls.__name__}__UNIQUE_FIELDS") or data.get(f"{kls.__name__}__UNIQUE_KEYS")
        if not field_names and hasattr(self, "seed_data") and isinstance(self.seed_data, dict):
            field_names = self.seed_data.get(f"{kls.__name__}__UNIQUE_FIELDS") or self.seed_data.get(
                f"{kls.__name__}__UNIQUE_KEYS"
            )

        if not field_names:
            field_names = self._model_wise_unique_fields.get(kls.__name__, None)

        if not field_names:
            return None

        field_map = {}
        for field_name in field_names:
            parts = field_name.split("__")
            val = data
            for part in parts:
                if isinstance(val, dict):
                    val = val.get(part)
                elif hasattr(val, part):
                    val = getattr(val, part)
                else:
                    val = None
                    break

            if val is not None:
                field_map[field_name] = val

        return field_map

    def classify_fields(self, kls: type[models.Model], data: dict = None) -> tuple[dict, dict]:
        """Split fields into lookup matchers (uniques) and remaining payload fields (defaults)."""
        unique_fields_map = self.get_unique_fields(kls, data) or {}
        defaults = {k: v for k, v in data.items() if k not in unique_fields_map}
        return unique_fields_map, defaults

    def init_obj(self, kls: models.Model, data: dict = None) -> models.Model:
        """Initialize an in-memory object, fetching from database if a unique match exists."""
        filters = None
        if pk := data.get("pk") or data.get("id"):
            filters = {"pk": pk}
        elif unique_field_map := self.get_unique_fields(kls, data):
            filters = unique_field_map
        else:
            return kls()

        try:
            instance = kls.objects.using(self._default_database).get(**filters)
        except kls.DoesNotExist:
            instance = kls()

        return instance

    def _create_object(self, kls: models.Model = None, data: dict = None) -> models.Model:
        data = data or self.model_data
        kls = kls or getattr(self, "_model", None)

        instance = self.init_obj(kls, data)
        if not instance:
            raise ObjectCreationException("Error in creating model object")

        m2m_fields = {}
        all_fields = kls._meta.get_fields(include_hidden=True)

        for field in all_fields:
            attname = getattr(field, "attname", None)
            if field.name not in data and (attname is None or attname not in data):
                continue

            if not field.is_relation:
                setattr(instance, field.name, data.get(field.name))
                continue

            if field.many_to_one or field.one_to_one:
                raw_value = data.get(field.name, data.get(attname) if attname else None)
                self._process_fk(instance, field, raw_value)

            if field.many_to_many:
                m2m_fields[field.name] = data.get(field.name)
                continue

        instance.save(using=self._default_database)
        self.process_m2m_fields(instance, m2m_fields)
        self.process_reverse_relations(instance, data)
        return instance

    def process_reverse_relations(self, instance: models.Model, data: dict):
        for rel in instance._meta.related_objects:
            accessor = rel.get_accessor_name()
            if accessor not in data:
                continue

            items = data.get(accessor)
            if not isinstance(items, (list, tuple)):
                items = (items,)

            related_model = rel.related_model
            fk_field_name = rel.field.name

            for item in items:
                if isinstance(item, models.Model):
                    setattr(item, fk_field_name, instance)
                    instance.save(using=self._default_database)
                elif isinstance(item, dict):
                    item[fk_field_name] = instance
                    self._create_object(kls=related_model, data=item)
                elif isinstance(item, (int, str)):
                    obj = related_model.objects.using(self._default_database).get(pk=item)
                    setattr(obj, fk_field_name, instance)
                    obj.save(using=self._default_database)

    def process_m2m_fields(self, instance: models.Model, m2m_data: dict):
        def _process_single_item(field: models.Field, data: typing.Any):
            if isinstance(data, (models.Model, str, int)):
                return data
            elif isinstance(data, dict):
                return self._create_object(kls=field.related_model, data=data)
            raise ObjectCreationException(f"Invalid M2M item: {data!r}")

        for field_name, raw_value in m2m_data.items():
            field = instance._meta.get_field(field_name)
            manager = getattr(instance, field_name)

            manager.clear()
            if not isinstance(raw_value, (list, tuple)):
                raw_value = (raw_value,)

            related_objs = []
            related_objs_to_fetch = []
            for item in raw_value:
                obj = _process_single_item(field, item)
                if isinstance(obj, (str, int)):
                    related_objs_to_fetch.append(obj)
                else:
                    related_objs.append(obj)

            if related_objs_to_fetch:
                objs = field.related_model.objects.filter(pk__in=related_objs_to_fetch)
                for obj in objs:
                    related_objs.append(obj)

            manager.add(*related_objs)

    def _process_fk(self, instance: models.Model, field: models.Field, raw_value: typing.Any):
        if isinstance(raw_value, models.Model):
            return setattr(instance, field.name, raw_value)
        elif isinstance(raw_value, dict):
            related_obj = self._create_object(kls=field.related_model, data=raw_value)
            return setattr(instance, field.name, related_obj)
        elif isinstance(raw_value, (int, str, type(None))):
            return setattr(instance, field.attname, raw_value)
        raise ObjectCreationException(f"Invalid value for FK '{field.name}': {raw_value!r}")

    def create_object(self, kls: type[models.Model] = None, data: typing.Union[dict, list] = None) -> object:
        """Atomic wrapper to initialize and save Django models."""
        if kls:
            self.set_model(kls)
        if data:
            self.set_model_data(data)

        model_class = getattr(self, "_model", None)
        model_data = getattr(self, "_model_data", None)

        if not model_class or model_data is None:
            raise ObjectCreationException("Data and model class are both required to create objects.")

        created_result = None
        with transaction.atomic():
            try:
                if isinstance(model_data, dict):
                    created_result = self._create_object()
                elif isinstance(model_data, list):
                    created_result = []
                    for i, _data in enumerate(model_data):
                        if not isinstance(_data, dict):
                            raise ObjectCreationException(f"Invalid data type {type(_data)} at index {i}")

                        self._model_data = _data
                        obj = self._create_object()
                        created_result.append(obj)
                else:
                    raise ObjectCreationException(f"Invalid data type: {type(model_data)}")
            except Exception as e:
                raise ObjectCreationException(f"Error creating object for {model_class.__name__}") from e

        self._model = None
        self._model_data = None
        return created_result


class BaseSeeder(ABC, ObjectCreationMixin):
    """The Base Seeder class implementing the Template Method pattern execution skeleton."""

    _register = True
    _file_prefix: typing.Optional[str] = None

    model: type[models.Model] = None
    depends_on: list[type["BaseSeeder"]] = []

    def __init_subclass__(cls):
        super().__init_subclass__()

        # Auto register every base class until explicitly un-registered.
        if getattr(cls, "_register", True):
            seeder_registry.register(cls)

    @property
    def scope(self) -> str:
        if getattr(self, "_scope", None) is not None:
            return self._scope

        if self.model:
            self._scope = self._auto_detect_scope()
            return self._scope
        
        return Scope.PUBLIC

    @scope.setter
    def scope(self, value):
        self._scope = value

    @property
    def data_source(self) -> DataSource:
        if getattr(self, "_data_source", None) is not None:
            return self._data_source
        if self.model:
            self._data_source = self._auto_detect_data_source()
            return self._data_source
        return None

    @data_source.setter
    def data_source(self, value):
        self._data_source = value

    @classmethod
    def _auto_detect_scope(cls) -> str:
        if not cls.model:
            return Scope.PUBLIC

        app_label = cls.model._meta.app_label
        app_config = None
        for app in settings.INSTALLED_APPS:
            if app.split(".")[-1] == app_label:
                app_config = app
                break

        is_shared = app_config in getattr(settings, "SHARED_APPS", [])
        is_tenant = app_config in getattr(settings, "TENANT_APPS", [])

        if is_shared and not is_tenant:
            return Scope.PUBLIC

        return Scope.PER_TENANT

    @classmethod
    def _auto_detect_data_source(cls) -> DataSource:
        path = cls._find_json_file()
        return FixtureSource(path)

    @classmethod
    def _find_json_file(cls) -> str:
        scope_val = getattr(cls, "_scope", None)
        if scope_val is None:
            scope_val = cls._auto_detect_scope()

        subfolder = "public" if scope_val == Scope.PUBLIC else "tenant"

        base_dir = Path(settings.APP_DIR) / "setup/local_setup/data/dev" / subfolder

        model_name = cls.model.__name__
        model_name_snake = re.sub(r"(?<!^)(?=[A-Z])", "_", model_name).lower()

        prefix = getattr(cls, "_file_prefix", None)
        filenames = []
        if prefix:
            filenames.append(f"{prefix}_{model_name}.json")
            filenames.append(f"{prefix}_{model_name_snake}.json")
            filenames.append(f"{prefix}.json")

        filenames.append(f"{model_name}.json")
        filenames.append(f"{model_name_snake}.json")

        for filename in filenames:
            path = base_dir / filename
            if path.exists():
                return str(path)
            if base_dir.exists():
                for subpath in base_dir.rglob(filename):
                    return str(subpath)

        root_data_dir = Path(settings.APP_DIR) / "setup/local_setup/data"
        for filename in filenames:
            path = root_data_dir / filename
            if path.exists():
                return str(path)
            if root_data_dir.exists():
                for subpath in root_data_dir.rglob(filename):
                    return str(subpath)

        return str(base_dir / f"{model_name_snake}.json")

    @property
    def seeder_data(self) -> typing.Any:
        """Data for seeder"""
        if getattr(self, "_seed_data", None) is not None:
            return self._seed_data

        if self.data_source:
            self._seed_data = self.data_source.load()
            return self._seed_data

        return None

    def get_data_for_model(self, model_name: str) -> typing.Union[list, dict, None]:
        """Get data for current model under execution for given data source.

        Args:
            model_name (str): Name of the model to load data from.

        Returns:
            Data for that model in seeder data.
        """
        if not self.seeder_data:
            return None

        if isinstance(self.seeder_data, dict):
            possible_keys = [
                model_name,
                f"{model_name}s",
                model_name.lower(),
                f"{model_name.lower()}s",
            ]
            for key in possible_keys:
                if key in self.seeder_data:
                    return self.seeder_data[key]
            return None

        if isinstance(self.seeder_data, list):
            results = []
            for item in self.seeder_data:
                if isinstance(item, dict):
                    possible_keys = [
                        model_name,
                        f"{model_name}s",
                        model_name.lower(),
                        f"{model_name.lower()}s",
                    ]
                    for key in possible_keys:
                        if key in item:
                            val = item[key]
                            if isinstance(val, list):
                                results.extend(val)
                            else:
                                results.append(val)
                            break

            if len(results) == 1:
                return results[0]

            return results if results else None

        return self.seeder_data

    def pre_seeding_hooks(self, data: list[dict]):
        """Pre hook for any pre-seeding logic"""
        pass

    def post_seeding_hook(self, objects):
        """Post hook for any post-seeding logic"""
        pass

    def seed(self) -> None:
        """Default seeding implementation that creates/updates database records."""
        if not self.model:
            raise SeederException("No model defined for seeder class.")

        data = self.get_data_for_model(self.model.__name__)
        if data is None:
            LOGGER.warning(
                "[%s] No matching seed data found for model %s", self.__class__.__name__, self.model.__name__
            )
            return

        self.pre_seeding_hooks(data)

        try:
            objects = self.create_object(self.model, data)
        except Exception as e:
            raise e

        return self.post_seeding_hook(objects)

    def run(self, schema_name: str) -> None:
        """The invariant Template Method running schema switching, logging, and database execution logs."""
        LOGGER.info("[%s] Seeder execution started on schema: %s", self.__class__.__name__, schema_name)

        if self._already_executed(schema_name):
            LOGGER.info(
                "[%s] Already successfully executed on schema: %s. Skipping.", self.__class__.__name__, schema_name
            )
            return

        try:
            with schema_context(schema_name):
                with transaction.atomic():
                    self.seed()

            self._log_execution_status(schema_name, "SUCCESS")
            LOGGER.info("[%s] Seeder execution succeeded on schema: %s", self.__class__.__name__, schema_name)

        except Exception as e:
            LOGGER.error("[%s] Seeder execution failed on schema %s: %s", self.__class__.__name__, schema_name, str(e))
            try:
                self._log_execution_status(schema_name, "FAILED")
            except Exception as inner_err:
                LOGGER.error("Failed to write failure log: %s", inner_err)
            raise e

    def _already_executed(self, schema_name: str) -> bool:
        try:
            with schema_context(schema_name):
                return SeederExecutionLog._base_manager.filter(
                    seeder_name=self.__class__.__name__, schema_name=schema_name, status="SUCCESS", is_removed=False
                ).exists()
        except Exception:
            return False

    def _log_execution_status(self, schema_name: str, status: str) -> None:
        with schema_context(schema_name):
            SeederExecutionLog._base_manager.update_or_create(
                seeder_name=self.__class__.__name__,
                schema_name=schema_name,
                defaults={"status": status, "is_removed": False},
            )

    @staticmethod
    def correct_file_path(file_path: str):
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
        if len(split := file_path.split(".")) > 1:
            return split[-1]
        return "txt"

    @staticmethod
    def load_from_file(path: str, file_type: str = "txt"):
        if not path:
            raise SeederException("`path` is required to load a file.")

        if not os.path.exists(path):
            raise SeederException(f"File not found at {path}")

        if file_type not in ["txt", "json", "html"]:
            raise SeederException(f"Invalid file type {file_type}")

        data = None
        with open(file=path, encoding="utf-8") as f:
            if file_type in ["txt", "html"]:
                data = f.read()
            elif file_type == "json":
                data = json.load(f)

        return data

    def load_file(self, file_path: str, file_type: str = "txt"):
        file_path = self.correct_file_path(file_path)
        file_type = self.file_type_from_path(file_path)
        content = self.load_from_file(file_path, file_type)
        return content

    def load_file_fields(self, val: str, field: str, resolved_fields: dict):
        content = self.load_file(val)
        resolved_fields[field] = content
        return resolved_fields
