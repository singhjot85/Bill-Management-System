import json
from typing import Any
from unittest.mock import MagicMock, mock_open, patch

import pytest
from django.core.exceptions import FieldDoesNotExist

from apps.setup.local_setup.seeders.base_seeder import BaseSeeder, SeederException


class MockModel:
    """Mock model class for testing purpose."""

    pass


class MockSeeder(BaseSeeder):
    """Concrete implementation of BaseSeeder for testing."""

    label = "Mock"
    REGISTERY_KEY = "mock_seeder"

    def seed(self, *args, **kwargs):
        """Mock seed implementation."""
        pass


class TestBaseSeeder:
    """
    Unit tests for the BaseSeeder class.
    Validates core seeder functionality including atomicity, field filtering, and data loading.
    """

    def setup_method(self):
        """Initialize MockSeeder for each test."""
        self.seeder = MockSeeder(file_name="test.json")

    def test_run_success(self):
        """
        Test that run() triggers the seed() method within an atomic transaction.
        """
        self.seeder.seed = MagicMock()

        with patch("apps.setup.local_setup.seeders.base_seeder.transaction.atomic"):
            self.seeder.run()

        self.seeder.seed.assert_called_once()

    def test_run_failure(self):
        """
        Test that run() correctly captures exceptions and raises SeederException.
        """
        self.seeder.seed = MagicMock(side_effect=Exception("Seed failed"))

        with patch("apps.setup.local_setup.seeders.base_seeder.transaction.atomic"):
            with pytest.raises(SeederException) as excinfo:
                self.seeder.run()

        assert "Seed failed" in str(excinfo.value)

    def test_filter_model_fields(self):
        """
        Test that filter_model_fields accurately separates concrete fields from
        virtual fields and non-existent attributes.
        """
        mock_model: Any = MagicMock()
        mock_model.__name__ = "MockModel"
        mock_field_name = MagicMock(concrete=True)
        mock_field_virtual = MagicMock(concrete=False)

        def get_field(name: str):
            if name == "name":
                return mock_field_name
            if name == "virtual":
                return mock_field_virtual
            raise FieldDoesNotExist()

        mock_model._meta.get_field.side_effect = get_field

        fields = {"name": "test", "virtual": "v", "invalid": "inv"}

        # Scenario 1: Filter for concrete fields only
        filtered_concrete = BaseSeeder.filter_model_fields(mock_model, fields, only_concrete=True)
        assert filtered_concrete == {"name": "test"}

        # Scenario 2: Include attributes that exist on the model even if not fields
        mock_model.invalid = "exists"
        filtered_all = BaseSeeder.filter_model_fields(mock_model, fields, only_concrete=False)
        assert filtered_all == {"name": "test", "virtual": "v", "invalid": "inv"}

    def test_load_data_success(self, settings: Any):
        """
        Test that load_data correctly parses JSON files and utilizes
        the internal cache for subsequent calls.
        """
        settings.BASE_DIR = "/tmp"
        data = {"key": "value"}
        cache_key = "test_cache"

        with patch("builtins.open", mock_open(read_data=json.dumps(data))):
            with patch("os.path.exists", return_value=True):
                loaded_data = self.seeder.load_data("test.json", cache_key_name=cache_key)

        assert loaded_data == data
        assert getattr(self.seeder, cache_key) == data

        # Verify cache hit (should not trigger another file open)
        with patch("builtins.open", mock_open()) as mock_file:
            cached_data = self.seeder.load_data("test.json", cache_key_name=cache_key)
            assert cached_data == data
            mock_file.assert_not_called()

    def test_load_data_invalid_file(self):
        """
        Test that load_data raises an error when provided with a file
        name lacking a valid extension.
        """
        with pytest.raises(SeederException) as excinfo:
            self.seeder.load_data("invalid_file", cache_key_name="error")

        assert "Invalid file name" in str(excinfo.value)
