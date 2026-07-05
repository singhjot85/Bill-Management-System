from unittest.mock import patch

import pytest
from django.contrib.auth.models import Group, User
from django.core.cache import cache

from apps.customer_management.models import Customer, CustomerAddress
from apps.setup.local_setup.seeders.base_seeder import (
    ObjectCreationException,
    ObjectCreationMixin,
)
from apps.setup.models import Configurations
from tests.factories import ConfigurationsFactory


class DummyObjectCreation(ObjectCreationMixin):
    """A concrete class to instantiate ObjectCreationMixin for testing."""

    pass


class TestObjectCreationMixin:
    """
    Unit and integration tests for ObjectCreationMixin.
    """

    def setup_method(self):
        self.mixin = DummyObjectCreation()

    # --- Unit Tests for Properties and Setters ---

    def test_model_property__not_set__raises_exception(self):
        """mixin.model should raise ObjectCreationException if not set."""
        with pytest.raises(ObjectCreationException) as excinfo:
            _ = self.mixin.model
        assert "models.Model not define, please use `set_model`" in str(excinfo.value)

    def test_set_model__invalid_class__raises_exception(self):
        """set_model should raise ObjectCreationException if not a Django Model subclass."""
        with pytest.raises(ObjectCreationException) as excinfo:
            self.mixin.set_model(dict)  # Not a models.Model subclass
        assert "models.Model should be a subclass of" in str(excinfo.value)

    def test_set_model__valid_class__sets_model(self):
        """set_model should succeed when passing a valid Django Model subclass."""
        self.mixin.set_model(Configurations)
        assert self.mixin.model == Configurations

    def test_model_data_property__not_set__raises_exception(self):
        """mixin.model_data should raise ObjectCreationException if not set."""
        with pytest.raises(ObjectCreationException) as excinfo:
            _ = self.mixin.model_data
        assert "models.Model not define" in str(excinfo.value)

    def test_set_model_data__dict__sets_data(self):
        """set_model_data should directly set data when a dictionary is passed."""
        data = {"key": "value"}
        self.mixin.set_model_data(data)
        assert self.mixin.model_data == data

    def test_set_model_data__str_file_path__loads_correct_section(self):
        """set_model_data should load from file and parse the section for the model name."""
        self.mixin.set_model(Configurations)
        mock_data = {"Configurations": {"key": "value"}}

        with patch.object(self.mixin, "load_data_from_file", return_value=mock_data) as mock_load:
            self.mixin.set_model_data("fake_path.json")
            mock_load.assert_called_once_with("fake_path.json")
            assert self.mixin.model_data == {"key": "value"}

    def test_load_data_from_file__file_not_found__raises_exception(self):
        """load_data_from_file should raise ObjectCreationException if file does not exist."""
        with pytest.raises(ObjectCreationException) as excinfo:
            self.mixin.load_data_from_file("non_existent_file.json")
        assert "No data file found" in str(excinfo.value)

    def test_load_data_from_file__invalid_json__raises_exception(self):
        """load_data_from_file should raise ObjectCreationException if file has invalid JSON."""
        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.read_text", return_value="invalid_json"):
                with pytest.raises(ObjectCreationException) as excinfo:
                    self.mixin.load_data_from_file("fake.json")
                assert "Error reading data file" in str(excinfo.value)

    # --- Unit Tests for init_obj ---

    def test_init_obj__no_pk__returns_new_instance(self):
        """init_obj should return a new unsaved instance if no pk/id is in data."""
        instance = self.mixin.init_obj(Configurations, {})
        assert isinstance(instance, Configurations)
        assert instance._state.adding is True

    @pytest.mark.django_db
    def test_init_obj__existing_pk__returns_existing_instance(self):
        """init_obj should retrieve and return existing object if pk exists in DB."""
        config = ConfigurationsFactory(interface_type="test_interface", details={"foo": "bar"})
        instance = self.mixin.init_obj(Configurations, {"pk": config.pk})
        assert isinstance(instance, Configurations)
        assert instance.pk == config.pk
        assert instance.details == {"foo": "bar"}

    @pytest.mark.django_db
    def test_init_obj__non_existent_pk__returns_new_instance(self):
        """init_obj should return a new instance if pk is provided but not found in DB."""
        import uuid

        instance = self.mixin.init_obj(Configurations, {"pk": uuid.uuid4()})
        assert isinstance(instance, Configurations)
        assert instance._state.adding is True

    @pytest.mark.django_db
    def test_init_obj__unique_fields_in_data__returns_existing_instance(self):
        """init_obj should retrieve and return existing object if unique fields in data match a DB record."""
        config = ConfigurationsFactory(interface_type="unique_interface_data", details={"foo": "bar"})

        data = {"interface_type": "unique_interface_data", "Configurations__UNIQUE_FIELDS": ["interface_type"]}
        instance = self.mixin.init_obj(Configurations, data)
        assert isinstance(instance, Configurations)
        assert instance.pk == config.pk
        assert instance._state.adding is False

    @pytest.mark.django_db
    def test_init_obj__unique_fields_in_mixin_defaults__returns_existing_instance(self):
        """init_obj should retrieve and return existing object using default unique fields from mixin."""
        config = ConfigurationsFactory(interface_type="unique_interface_data", details={"test": "data"})

        data = {"interface_type": "unique_interface_data"}
        instance = self.mixin.init_obj(Configurations, data)
        assert isinstance(instance, Configurations)
        assert instance.pk == config.pk
        assert instance._state.adding is False

    @pytest.mark.django_db
    def test_init_obj__unique_fields_not_found__returns_new_instance(self):
        """init_obj should return a new instance if unique fields are specified but no match exists in DB."""
        data = {"interface_type": "non_existent_interface", "Configurations__UNIQUE_FIELDS": ["interface_type"]}
        instance = self.mixin.init_obj(Configurations, data)
        assert isinstance(instance, Configurations)
        assert instance._state.adding is True

    @pytest.mark.django_db
    def test_init_obj__unique_fields_ignored_if_pk_exists(self):
        """init_obj should prioritize lookup by pk if both pk and unique fields are provided."""
        config1 = ConfigurationsFactory(interface_type="interface1", details={"foo": "bar"})
        ConfigurationsFactory(interface_type="interface2", details={"foo": "baz"})

        data = {"pk": config1.pk, "interface_type": "interface2", "Configurations__UNIQUE_FIELDS": ["interface_type"]}
        instance = self.mixin.init_obj(Configurations, data)
        assert isinstance(instance, Configurations)
        assert instance.pk == config1.pk
        assert instance._state.adding is False

    @pytest.mark.django_db
    def test_get_unique_fields__unique_keys_key__returns_correct_fields(self):
        """get_unique_fields should support UNIQUE_KEYS key in data payload."""
        data = {"interface_type": "some_interface", "Configurations__UNIQUE_KEYS": ["interface_type"]}
        res = self.mixin.get_unique_fields(Configurations, data)
        assert res == {"interface_type": "some_interface"}

    @pytest.mark.django_db
    def test_get_unique_fields__nested_relationship__resolves_nested_field(self):
        """get_unique_fields should resolve double-underscore nested fields from dictionaries and models."""
        from apps.tenants.models import OrganizationBranding, OrganizationTenant

        tenant = OrganizationTenant(schema_name="my_nested_schema")
        data = {
            "organization": tenant,
            "phone": "99999",
            "OrganizationBranding__UNIQUE_FIELDS": ["organization__schema_name"],
        }
        res = self.mixin.get_unique_fields(OrganizationBranding, data)
        assert res == {"organization__schema_name": "my_nested_schema"}

    @pytest.mark.django_db
    def test_classify_fields__correctly_splits_uniques_and_defaults(self):
        """classify_fields should correctly classify data into uniques and defaults."""
        data = {
            "interface_type": "some_interface",
            "details": {"key": "val"},
            "Configurations__UNIQUE_FIELDS": ["interface_type"],
        }
        uniques, defaults = self.mixin.classify_fields(Configurations, data)
        assert uniques == {"interface_type": "some_interface"}
        assert defaults == {"details": {"key": "val"}, "Configurations__UNIQUE_FIELDS": ["interface_type"]}

    # --- Full Workflow Tests ---

    @pytest.mark.django_db
    def test_create_object__happy_path_single__creates_db_record(self):
        """Verify workflow of creating a single object without relations."""
        data = {"interface_type": "single_test_interface", "details": {"channels": ["email"]}}
        res = self.mixin.create_object(kls=Configurations, data=data)

        # Verify returned object
        assert isinstance(res, Configurations)
        assert res.pk is not None
        assert res.interface_type == "single_test_interface"
        assert res.details == {"channels": ["email"]}

        # Verify DB persistence
        config = Configurations.objects.get(pk=res.pk)
        assert config.interface_type == "single_test_interface"

    @pytest.mark.django_db
    def test_create_object__happy_path_list__creates_multiple_records(self):
        """Verify workflow of creating multiple objects from a list."""
        Configurations._base_manager.all().delete()
        cache.clear()

        data_list = [
            {"interface_type": "list_test_interface", "details": {"c": 1}},
            {"interface_type": "list_test_interface_2", "details": {"c": 2}},
        ]
        res = self.mixin.create_object(kls=Configurations, data=data_list)

        assert isinstance(res, list)
        assert len(res) == 2
        assert all(isinstance(obj, Configurations) for obj in res)
        assert res[0].details == {"c": 1}
        assert res[1].details == {"c": 2}

        assert Configurations.objects.all().count() == 2

    @pytest.mark.django_db
    def test_create_object__with_forward_foreign_key_relation(self):
        """Verify workflow where creating model with FK dict creates the related model first."""
        data = {
            "address_line_1": "456 Oak Ave",
            "city": "Metropolis",
            "customer": {"name": "Bruce Wayne", "email": "bruce@wayne.corp", "customer_type": "private"},
        }
        addr = self.mixin.create_object(kls=CustomerAddress, data=data)

        assert isinstance(addr, CustomerAddress)
        assert addr.pk is not None
        assert addr.address_line_1 == "456 Oak Ave"

        # Verify customer was created
        customer = addr.customer
        assert isinstance(customer, Customer)
        assert customer.pk is not None
        assert customer.name == "Bruce Wayne"
        assert customer.email == "bruce@wayne.corp"

    @pytest.mark.django_db
    def test_create_object__with_reverse_relation(self):
        """Verify workflow where creating main model with nested reverse relations creates both."""
        data = {
            "name": "Clark Kent",
            "email": "clark@dailyplanet.com",
            "customer_type": "private",
            "customer_addresses": [
                {"address_line_1": "123 Metropolis St", "is_primary": True},
                {"address_line_1": "456 Smallville Rd", "is_primary": False},
            ],
        }
        cust = self.mixin.create_object(kls=Customer, data=data)

        assert isinstance(cust, Customer)
        assert cust.pk is not None
        assert cust.name == "Clark Kent"

        # Verify addresses were created and attached
        addresses = list(cust.customer_addresses.all())
        assert len(addresses) == 2
        assert addresses[0].address_line_1 == "123 Metropolis St"
        assert addresses[0].is_primary is True
        assert addresses[1].address_line_1 == "456 Smallville Rd"
        assert addresses[1].is_primary is False

    @pytest.mark.django_db
    def test_create_object__with_many_to_many_relation(self):
        """Verify workflow where many_to_many fields are processed and attached properly."""
        # Create standard Group objects
        group1 = Group.objects.create(name="AdminGroup")
        group2 = Group.objects.create(name="UserGroup")

        # We can seed a User with many-to-many groups.
        data = {"username": "superman", "email": "superman@dc.com", "groups": [group1.pk, group2.pk]}

        user = self.mixin.create_object(kls=User, data=data)

        assert isinstance(user, User)
        assert user.pk is not None
        assert user.username == "superman"

        # Verify many-to-many associations
        groups = list(user.groups.all())
        assert len(groups) == 2
        assert group1 in groups
        assert group2 in groups

    @pytest.mark.django_db
    def test_create_object__m2m_creation_via_dict(self):
        """Verify workflow where nested dicts in many_to_many fields are created automatically."""
        data = {
            "username": "batman",
            "email": "batman@dc.com",
            "groups": [{"name": "JusticeLeague"}, {"name": "BatFamily"}],
        }

        user = self.mixin.create_object(kls=User, data=data)

        assert isinstance(user, User)
        groups = list(user.groups.all())
        assert len(groups) == 2
        names = [g.name for g in groups]
        assert "JusticeLeague" in names
        assert "BatFamily" in names

        # Verify DB records
        assert Group.objects.filter(name="JusticeLeague").exists()
        assert Group.objects.filter(name="BatFamily").exists()

    @pytest.mark.django_db
    def test_create_object__atomic_transaction_on_failure(self):
        """Verify that object creation is rolled back atomically if any error occurs."""
        data = {
            "name": "Arthur Curry",
            "email": "aquaman@atlantis.gov",
            "customer_type": "private",
            "customer_addresses": [
                {"address_line_1": "Atlantis Palace", "is_primary": True},
                {
                    "address_line_1": "Palace Gates",
                    "is_primary": False,
                    "postal_code": "this-is-not-an-integer",  # Trigger database DataError
                },
            ],
        }

        # Before running, verify counts
        assert Customer.objects.filter(email="aquaman@atlantis.gov").count() == 0

        with pytest.raises(ObjectCreationException):
            self.mixin.create_object(kls=Customer, data=data)

        # Verify that customer creation was rolled back completely
        assert Customer.objects.filter(email="aquaman@atlantis.gov").count() == 0
        assert CustomerAddress.objects.filter(address_line_1="Atlantis Palace").count() == 0
