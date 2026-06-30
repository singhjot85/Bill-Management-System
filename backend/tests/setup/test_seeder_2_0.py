from unittest.mock import MagicMock, mock_open, patch

import pytest
from django.db import models

from apps.setup.seeder.base import BaseSeeder, Scope
from apps.setup.seeder.runner import topological_sort
from apps.setup.seeder.sources import (
    FactorySource,
    FixtureSource,
    TenantAwareFixtureSource,
)


class DummyModel(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = "setup"


class DummySeeder(BaseSeeder):
    model = DummyModel
    scope = Scope.PUBLIC
    depends_on = []

    def seed(self, data, schema_name):
        self.create_object(DummyModel, data)


class DependentSeeder(BaseSeeder):
    model = DummyModel
    scope = Scope.PER_TENANT
    depends_on = [DummySeeder]

    def seed(self, data, schema_name):
        pass


@pytest.mark.django_db
class TestSeederV2:
    def test_topological_sort(self):
        """Test topological sorting of seeders based on dependency graph."""
        order = topological_sort([DependentSeeder, DummySeeder])
        assert order == [DummySeeder, DependentSeeder]

    def test_topological_sort_circular_raises_error(self):
        """Test that circular dependencies in seeders raise a ValueError."""

        class CircularA(BaseSeeder):
            pass

        class CircularB(BaseSeeder):
            depends_on = [CircularA]

        CircularA.depends_on = [CircularB]

        with pytest.raises(ValueError, match="Circular dependency detected"):
            topological_sort([CircularA, CircularB])

    def test_fixture_source_load(self, settings):
        """Test standard JSON file loading by FixtureSource."""
        settings.APP_DIR = "/tmp"
        source = FixtureSource("test.json")
        with patch("builtins.open", mock_open(read_data='{"key": "value"}')):
            with patch("pathlib.Path.exists", return_value=True):
                data = source.load()
                assert data == [{"key": "value"}]

    def test_tenant_aware_fixture_source(self, settings):
        """Test schema-aware file loading by TenantAwareFixtureSource."""
        settings.APP_DIR = "/tmp"
        source = TenantAwareFixtureSource({"public": "public.json", "localngo": "ngo.json"})
        with patch("builtins.open", mock_open(read_data='{"schema": "success"}')):
            with patch("pathlib.Path.exists", return_value=True):
                with patch("django.db.connection.schema_name", "localngo"):
                    data = source.load()
                    assert data == [{"schema": "success"}]

    def test_factory_source_load(self):
        """Test model instance generation by FactorySource."""
        mock_factory = MagicMock()
        mock_factory.build.return_value = {"id": 1}
        source = FactorySource(mock_factory, batch_size=2, arg="val")

        results = source.load()
        assert len(results) == 2
        mock_factory.build.assert_called_with(arg="val")

    def test_base_seeder_idempotency(self):
        """Test that BaseSeeder skips execution if a successful execution log is found."""
        seeder = DummySeeder()
        seeder.seed = MagicMock()
        seeder.data_source = MagicMock()
        seeder.data_source.load.return_value = {"name": "test_tenant"}

        # Run 1: Runs successfully
        seeder.run("public")
        seeder.seed.assert_called_once()

        # Run 2: Skipped (due to SUCCESS record in database)
        seeder.seed.reset_mock()
        seeder.run("public")
        seeder.seed.assert_not_called()

    def test_auto_detect_dependencies(self):
        """Test that ForeignKey relations are automatically resolved as seeder dependencies."""
        from apps.setup.seeder.runner import resolve_all_dependencies
        from apps.tenants.models import OrganizationBranding, OrganizationTenant

        class MockBrandingSeeder(BaseSeeder):
            model = OrganizationBranding
            _register = False

        class MockTenantSeeder(BaseSeeder):
            model = OrganizationTenant
            _register = False

        resolve_all_dependencies([MockBrandingSeeder, MockTenantSeeder])
        assert MockTenantSeeder in MockBrandingSeeder.resolved_dependencies

    def test_auto_detect_scope(self):
        """Test that scope is correctly auto-detected based on application types."""
        from apps.tenants.models import OrganizationTenant

        class MockTenantSeeder(BaseSeeder):
            model = OrganizationTenant
            _register = False

        seeder = MockTenantSeeder()
        assert seeder.scope == Scope.PUBLIC

    def test_fuzzy_matching_data_extraction(self):
        """Test that get_data_for_model handles case-insensitive and plural fuzzy matching."""

        class MockUserSeeder(BaseSeeder):
            model = DummyModel
            _register = False

        seeder = MockUserSeeder()

        # Plural match
        seeder._seed_data = {"DummyModels": [{"name": "Bruce"}]}
        assert seeder.get_data_for_model("DummyModel") == [{"name": "Bruce"}]

        # Lowercase match
        seeder._seed_data = {"dummymodel": {"name": "Clark"}}
        assert seeder.get_data_for_model("DummyModel") == {"name": "Clark"}

        # List mapping match
        seeder._seed_data = [{"DummyModels": {"name": "Diana"}}]
        assert seeder.get_data_for_model("DummyModel") == {"name": "Diana"}
