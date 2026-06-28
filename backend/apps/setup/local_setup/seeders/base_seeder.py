import json
import logging
import os
import typing
from abc import ABC, abstractmethod
from pathlib import Path

from django.conf import settings
from django.core.exceptions import FieldDoesNotExist
from django.db import models, transaction
from django_tenants.utils import schema_context

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

    @property
    def model(self) -> typing.Optional[models.Model]:
        """models.Model set for current object processing"""

        if hasattr(self, "_model"):
            return getattr(self, "_model")

        raise ObjectCreationException("models.Model not define, please use `set_model` to declare a model to process.")

    def set_model(self, kls: models.Model):
        """Set the model instance to the mixin object

        Args:
            kls (models.Model): django models.Model class for which the object is to be created.

        Raises:
            ObjectCreationException
        """

        if not isinstance(kls, models.Model):
            raise ObjectCreationException("models.Model should be an instance of `django.db.models.models.Model`.")

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
            data = self.load_data_from_file(data).get(self.model)

        self._model_data = data

    def init_obj(self, kls: models.Model, data: dict = None) -> models.Model:
        """Initialize an in-memory object

        Args:
            kls (models.Model): Class for which model is to be created.
            data (dict): Data to fetch pk/unique key(s), this step ensure(s) no de-duplication.

        Returns:
            instance (object): In-memory object of given kls class.
        """
        pk = data.get("pk") or data.get("id")

        if not pk:
            return kls()

        instance = None
        try:
            instance = kls.objects.using(self._default_database).get(pk=pk)
        except kls.DoesNotExist:
            instance = kls()

        return instance

    def _create_object(self, kls: models.Model = None, data: dict = None) -> models.Model:
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
        all_fields: list[models.Field] = self.model._meta.get_fields(include_hidden=True)

        for field in all_fields:
            # If field not in data continue to next field
            if field.name not in data and field.attname not in data:
                continue

            # Non-relation fields are set diectly
            if not field.is_relation:
                setattr(instance, field.name, data.get(field.name))
                continue

            # forawrd relation's i.e. whose FK.id lives in model's table, is also saved directly
            if field.many_to_one or field.one_to_one:
                raw_value = data.get(field.name, data.get(field.attname))
                self._process_fk(instance, field, raw_value)

            # m2m fields are saved in a dict to be used later
            if field.many_to_many:
                m2m_fields[field.name] = data.get(field.name)
                continue

        instance.save(using=self._default_database)
        self.process_m2m_fields(instance, m2m_fields)
        self.process_reverse_relations(instance, data)

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
                if isinstance(models.Model):
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
                if isinstance(obj, str):
                    related_objs_to_fetch.append(obj)
                related_objs.append(obj)

            if related_objs_to_fetch:
                objs = field.related_model.objects.filter(pk__in=related_objs_to_fetch)
                for obj in objs:
                    related_objs.append(obj)

            manager.add(*related_objs)

    def _process_fk(self, instance: models.Model, field: models.Field, raw_value: typing.Any):
        """Process many_to_one and one_to_one, this is helper method used in object creation"""

        if isinstance(raw_value, models.Model):
            return setattr(instance, field.name, raw_value)

        elif instance(raw_value, dict):
            related_obj = self._create_object(kls=field.related_model, data=raw_value)
            return setattr(instance, field.name, related_obj)

        elif isinstance(raw_value, (int, str, type(None))):
            return setattr(instance, field.attname, raw_value)

        raise ObjectCreationException(f"Invalid value for FK '{field.name}': {raw_value!r}")

    def create_object(self, kls: models.Model = None, data: typing.Union[dict, str] = None) -> object:
        """Create a model from given object data. You can either pass data to this method or set it using `set_data`

        Args:
            kls (models.Model, optional): django models.Model class for which the object is to be created.
            data (dict, optional): Data to be used for object creation or path to the data file to be used

        Returns:
            Instance of the created object.

        Raises:
            ObjectCreationException
        """
        if kls:
            self.set_model(kls)
        if data:
            self.set_model_data(data)

        if not all(data, kls):
            raise ObjectCreationException(
                "Data and model class both are required to be set on mixin object for processing."
            )

        with transaction.atomic():
            try:
                if isinstance(data, dict):  # Single object creation
                    self._create_object()

                elif isinstance(data, list):  # Multi object creation
                    for i, _data in enumerate(self.model_data):
                        if not isinstance(data, dict):
                            raise ObjectCreationException(f"Invalid data type {type(_data)} at position {i}")

                        try:
                            self._model_data = _data
                            self.create_object()
                        except Exception as e:
                            raise ObjectCreationException(f"Failed creating object for index: {i}") from e

                else:
                    raise ObjectCreationException(f"Invalid data type: {type(data)}") from None
            except Exception as e:
                raise ObjectCreationException(f"Error while creating object for {kls.__name__}") from e

        self._model = None
        self._model_data = None


class BaseSeeder(ABC, ObjectCreationMixin):
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
        content = self.load_file()
        resolved_fields[field] = content

    def get_unique_fields(self, model_name: str) -> list:
        """Get unique keys for the model,
        We provide freedom to define unique keys that can be set in data so that object creation remains idempotent
        These are generally fields that are not unique on database level.

        Args:
            model_name (str): models.Model for which unique fields are to be fetched.

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

    def classify_fields(self, model_name: typing.Union[str, typing.Any], filtered_fields: str) -> tuple[dict, dict]:
        """Classify into defaults and uniques"""
        if not isinstance(model_name, str):
            model_name = model_name.__name__

        unique_keys = self.get_unique_fields(model_name)
        uniques = {k: v for k, v in filtered_fields.items() if k in unique_keys}
        defaults = {k: v for k, v in filtered_fields.items() if k not in unique_keys}

        return uniques, defaults
