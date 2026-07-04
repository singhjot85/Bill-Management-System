import json
import logging
import os
import typing
from abc import ABC, abstractmethod
from pathlib import Path

from django.conf import settings
from django.core.exceptions import FieldDoesNotExist
from django.db import models, transaction
from django_tenants.utils import get_public_schema_name, schema_context

from apps.tenants.models import OrganizationTenant

LOGGER = logging.getLogger()


class SeederException(Exception):
    """General Exception raised when from seeder."""

    pass


class ObjectCreationException(Exception):
    """General Exception raised when creating an object."""

    pass


class ObjectCreationMixin:
    """This mixin will be used to create objects from given data in json file
    Create a mixin so that it can easly be lifter to seeder2.0
    """

    _model: models.Model
    _model_data: dict
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
        """models.Model set for current object processing"""

        if hasattr(self, "_model"):
            return getattr(self, "_model")

        raise ObjectCreationException("models.Model not define, please use `set_model` to declare a model to process.")

    def set_model(self, kls: type[models.Model]):
        """Set the model instance to the mixin object

        Args:
            kls (type[models.Model]): django models.Model class for which the object is to be created.

        Raises:
            ObjectCreationException
        """

        if not (isinstance(kls, type) and issubclass(kls, models.Model)):
            raise ObjectCreationException("models.Model should be a subclass of `django.db.models.Model`.")

        self._model = kls

    @property
    def model_data(self) -> typing.Union[dict, str]:
        """models.Model set for current object processing"""

        if hasattr(self, "_model_data"):
            return getattr(self, "_model_data")

        raise ObjectCreationException("models.Model not define, please use `set_model` to declare a model to process.")

    def load_data_from_file(self, file_path: str):
        """Load data from a data file"""
        path_obj = Path(file_path)
        if not path_obj.exists():
            raise ObjectCreationException(f"No data file found, Invalid Path: {file_path}")

        try:
            return json.loads(path_obj.read_text())
        except Exception as e:
            raise ObjectCreationException(f"Error reading data file: {str(e)}") from e

    def set_model_data(self, data: typing.Union[dict, str]) -> typing.Union[list, dict]:
        """Set the model data to the mixin object

        Args:
            data (dict, str): Data to be used for object creation or path to the data file to be used
        """
        if isinstance(data, str):
            data = self.load_data_from_file(data).get(self.model.__name__)

        self._model_data = data

    def get_unique_fields(self, kls: type[models.Model], data: dict = None) -> dict:
        """Get unique fields which prevent de-duped object creation,
        if the data from those fields match the data in current json, we don't create new object
        """
        field_names = data.get(f"{kls.__name__}__UNIQUE_FIELDS") or data.get(f"{kls.__name__}__UNIQUE_KEYS")
        if not field_names and hasattr(self, "seed_data") and self.seed_data:
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
        """Classify fields into unique fields (uniques) and remaining fields (defaults)"""
        unique_fields_map = self.get_unique_fields(kls, data) or {}
        defaults = {k: v for k, v in data.items() if k not in unique_fields_map}
        return unique_fields_map, defaults

    def init_obj(self, kls: models.Model, data: dict = None) -> models.Model:
        """Initialize an in-memory object

        Args:
            kls (models.Model): Class for which model is to be created.
            data (dict): Data to fetch pk/unique key(s), this step ensure(s) no de-duplication.

        Returns:
            instance (object): In-memory object of given kls class.
        """

        filters = None
        if pk := data.get("pk") or data.get("id"):
            filters = {"pk": pk}
        elif unique_field_map := self.get_unique_fields(kls, data):
            filters = unique_field_map
        else:
            return kls()

        instance = None
        try:
            instance = kls.objects.using(self._default_database).get(**filters)
        except kls.DoesNotExist:
            instance = kls()

        return instance

    def _set_field_attr(self, model_instance: models.Model, field_name: str, value: typing.Any) -> None:
        """
        Some fields like User.password, file_fields shouldn't be set directly using setattr
        They need their own seperate logic, this method gives us freedom for that

        Args:
            model_instance (models.Model): Current object under execution.
            field_name (str): Name of the field.
            value (Any): Data for that field from entire data object.
        """
        method_name = f"setter_{field_name}"
        if hasattr(self, method_name):
            return getattr(self, method_name)(model_instance, field_name, value)

        setattr(model_instance, field_name, value)

    def _create_object(self, kls: type[models.Model] = None, data: dict = None) -> models.Model:
        """This method create(s) one object at a time from given data and class.

        Args:
            kls (models.Model, optional): Class of the model to create object from.
                By, default uses self.
            data (dict, optional): Data for the object to be created.

        Returns:
            Object created from the given data, persistent in database.

        Raises:
            ObjectCreationException
        """
        data = data or self.model_data
        kls = kls or self.model

        instance = self.init_obj(kls, data)

        if not instance:
            raise ObjectCreationException("Error in creating model object")

        m2m_fields = {}
        all_fields: list[models.Field] = kls._meta.get_fields(include_hidden=True)

        for field in all_fields:
            # If field not in data continue to next field
            attname = getattr(field, "attname", None)
            if field.name not in data and (attname is None or attname not in data):
                continue

            # Non-relation fields are set diectly
            if not field.is_relation:
                # setattr(instance, field.name, data.get(field.name))
                self._set_field_attr(instance, field.name, data.get(field.name))

            # forawrd relation's i.e. whose FK.id lives in model's table, is also saved directly
            if field.many_to_one or field.one_to_one:
                raw_value = data.get(field.name, data.get(attname) if attname else None)
                self._process_fk(instance, field, raw_value)

            # m2m fields are saved in a dict to be used later
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
                    # setattr(item, fk_field_name, instance)
                    self._set_field_attr(item, fk_field_name, instance)
                    instance.save(using=self._default_database)

                elif isinstance(item, dict):
                    item[fk_field_name] = instance
                    self._create_object(kls=related_model, data=item)

                elif isinstance(item, (int, str)):
                    obj = related_model.objects.using(self._default_database).get(pk=item)
                    # setattr(obj, fk_field_name, instance)
                    self._set_field_attr(obj, fk_field_name, instance)
                    obj.save(using=self._default_database)

    def process_m2m_fields(self, instance: models.Model, m2m_data: dict):
        """Process many-to-many fields, fetch a related manager for m2m field and attach all objects to the instance using `manager.add`
        Attach object to instace means u create a (obj_id, instance_id) in the m2m table.

        Args:
            instance: (models.Model): Model object on which the m2m fields are to be attached.
            m2m_data (dict): Data for the m2m fields.

        Raises:
            ObjectCreationException
        """

        def _process_single_item(field: models.Field, data: typing.Any):
            """Process a single m2m item at once."""
            if isinstance(data, (models.Model, str, int)):
                return data
            elif isinstance(data, dict):
                return self._create_object(kls=field.related_model, data=data)
            raise ObjectCreationException(f"Invalid M2M item: {item!r}")

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
        """Process many_to_one and one_to_one, this is helper method used in object creation"""
        if isinstance(raw_value, models.Model):
            # return setattr(instance, field.name, raw_value)
            return self._set_field_attr(instance, field.name, raw_value)

        elif isinstance(raw_value, dict):
            related_obj = self._create_object(kls=field.related_model, data=raw_value)
            # return setattr(instance, field.name, related_obj)
            return self._set_field_attr(instance, field.name, related_obj)

        elif isinstance(raw_value, (int, str, type(None))):
            # return setattr(instance, field.attname, raw_value)
            return self._set_field_attr(instance, field.attname, raw_value)

        raise ObjectCreationException(f"Invalid value for FK '{field.name}': {raw_value!r}")

    def create_object(self, kls: type[models.Model] = None, data: typing.Union[dict, list, str] = None) -> object:
        """Create a model from given object data. You can either pass data to this method or set it using `set_data`

        Args:
            kls (type[models.Model], optional): django models.Model class for which the object is to be created.
            data (dict, list, str, optional): Data to be used for object creation or path to the data file to be used

        Returns:
            Instance of the created object.

        Raises:
            ObjectCreationException
        """
        LOGGER.debug("Starting object creation for >>> %s", kls.__name__)

        if kls:
            self.set_model(kls)
        if data:
            self.set_model_data(data)

        model_class = getattr(self, "_model", None)
        model_data = getattr(self, "_model_data", None)

        if not model_class or model_data is None:
            raise ObjectCreationException(
                "Data and model class both are required to be set on mixin object for processing."
            )

        created_result = None
        with transaction.atomic():
            try:
                if isinstance(model_data, dict):  # Single object creation
                    created_result = self._create_object()

                elif isinstance(model_data, list):  # Multi object creation
                    created_result = []
                    for i, _data in enumerate(model_data):
                        if not isinstance(_data, dict):
                            raise ObjectCreationException(f"Invalid data type {type(_data)} at position {i}")

                        try:
                            self._model_data = _data
                            obj = self._create_object()
                            created_result.append(obj)
                        except Exception as e:
                            raise ObjectCreationException(f"Failed creating object for index: {i}") from e

                else:
                    raise ObjectCreationException(f"Invalid data type: {type(model_data)}") from None
            except Exception as e:
                raise ObjectCreationException(f"Error while creating object for {model_class.__name__}") from e

        LOGGER.debug("Object creation successfull for >>> %s, obj >>>", kls.__name__, created_result)
        self._model = None
        self._model_data = None
        return created_result


class BaseSeeder(ABC, ObjectCreationMixin):
    """Base Seeder Templae to be used by each seeder."""

    label: str = ""
    DATA_FILES_PATH = "setup/local_setup/data"
    REGISTERY_KEY = ""

    initial = False
    depends_on = []

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
        if len(split := file_path.split(".")) > 1:
            return split[-1]

        return "txt"

    @staticmethod
    def load_from_file(path: str, file_type: str = "txt"):
        """Load Data from a file
        Args:
            path (str): Complete file path.
            type (str, optional): Type of data to load.
                txt | json

        Raises:
            SeederException
        """
        if not path:
            raise SeederException("`path` is required to load a file.")

        if not os.path.exists(path):
            raise SeederException(f"File not found at {path}")

        if file_type not in ["txt", "json", "html"]:
            raise SeederException(f"Invalid file type {file_type}")

        data = None
        with open(file=path, mode="r+", encoding="utf-8") as f:
            if file_type in ["txt", "html"]:
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

    @classmethod
    def run_in_schema(self) -> str:
        """Specify the tenant in which the seeder should run

        Override for seeder specific tenant switching.
        """
        return get_public_schema_name()

    def validate_schema(self, schema_name: str) -> str:
        """Validate's if the schema is a valid schema or not.

        Args:
            schema_name (str): Schema to validate

        Returns:
            schema_name (str): Validated schema

        Raises:
            SeederException
        """
        if schema_name == get_public_schema_name():
            return True

        try:
            with schema_context(get_public_schema_name()):
                return OrganizationTenant.objects.get(schema_name=schema_name).schema_name
        except OrganizationTenant.DoesNotExist as e:
            raise SeederException("Schema is not available yet, create it first to run the seeder") from e
        except Exception as e:
            raise SeederException("Unknown error occurred while looking up schema: %s", schema_name) from e

    def pre_run_validations(self, *args, **kwargs):
        """Pre Validation hooks for seed.run"""
        schema_name = self.run_in_schema()
        self.validate_schema(schema_name)

        return schema_name

    def run(self, *args, **kwargs):
        """Main caller for each seeder, stays in base, rarely overriden"""
        LOGGER.info("[%s] Running Seeder...", self.label)

        try:
            schema_name = self.pre_run_validations()

            if not schema_name:
                raise SeederException("Schema not found...")

            with schema_context(schema_name):
                with transaction.atomic():  # Atomicity
                    # Idempotency, inside the seed (to be taken care of always).
                    self.seed(*args, **kwargs)

                self.post_run_validations()
        except Exception as e:
            LOGGER.error("[%s] Seeder run failed.", self.label)
            raise SeederException(str(e)) from e

        LOGGER.info("[%s] Seeder ran successfully.", self.label)

    def post_run_validations(self, *args, **kwargs):
        """Pre Validation hooks for seed.run"""
        pass

    @staticmethod
    def filter_model_fields(
        model: type[models.Model], fields: dict[str, typing.Any], only_concrete: bool = True
    ) -> dict[str, typing.Any]:
        """Filter models.Model fields from given fields, cleaner for raw field names.

        Args:
            model: models.Model Class.
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
                field: models.Field = model._meta.get_field(key)
                if only_concrete and not field.concrete:
                    continue
                filtered[key] = value

            except FieldDoesNotExist:
                if only_concrete:
                    # Silently skip non-existent fields in strict mode
                    LOGGER.debug("models.Field [%s] doesn't exist on model [%s], skipping", key, model.__name__)
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
        content = self.load_file(val)
        resolved_fields[field] = content
        return resolved_fields
