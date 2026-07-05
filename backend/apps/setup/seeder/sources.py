import json
import typing
from pathlib import Path

from django.conf import settings
from django.db import connection

from apps.setup.seeder.exceptions import SeederException


class DataSource(typing.Protocol):
    def load(self) -> list[dict]:
        """Load and return structured data for seeding."""
        ...


class FixtureSource:
    """Strategy to load data from standard JSON files."""

    def __init__(self, file_path: typing.Union[str, list[str], tuple[str]]):
        self.file_paths = [file_path] if isinstance(file_path, str) else list(file_path)

    def _load_single(self, path_str: str) -> typing.Any:
        possible_paths = [
            Path(path_str),
            Path(settings.APP_DIR) / path_str,
            Path(settings.APP_DIR) / "setup/seeder/data" / path_str,
            Path(settings.APP_DIR) / "setup/local_setup/data" / path_str,
        ]

        full_path = None
        for path in possible_paths:
            if path.exists():
                full_path = path
                break

        if not full_path:
            raise SeederException(f"Fixture file not found: {path_str}")

        try:
            with open(full_path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise SeederException(f"Failed to load fixture {path_str}: {e}") from e

    def load(self) -> list[dict]:
        results = []
        for path_str in self.file_paths:
            data = self._load_single(path_str)
            if isinstance(data, list):
                results.extend(data)
            else:
                results.append(data)
        return results


class TenantAwareFixtureSource:
    """Strategy to load data from standard JSON files based on current active schema context."""

    def __init__(self, schema_to_file_map: dict):
        self.schema_to_file_map = schema_to_file_map

    def load(self) -> list[dict]:
        schema_name = connection.schema_name
        file_name = self.schema_to_file_map.get(schema_name)

        if not file_name:
            file_name = self.schema_to_file_map.get("default")
            if not file_name:
                raise SeederException(f"No fixture file mapped for schema context: {schema_name}")

        possible_paths = [
            Path(settings.APP_DIR) / file_name,
            Path(settings.APP_DIR) / "setup/seeder/data" / file_name,
            Path(settings.APP_DIR) / "setup/local_setup/data" / file_name,
        ]

        full_path = None
        for path in possible_paths:
            if path.exists():
                full_path = path
                break

        if not full_path:
            raise SeederException(f"Fixture file not found: {file_name}")

        data = None
        try:
            with open(full_path, encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            raise SeederException(f"Failed to load fixture {file_name}: {e}") from e

        return data if isinstance(data, list) else [data]


class FactorySource:
    """Strategy to generate dynamic mock data using a Factory Boy factory class."""

    def __init__(self, factory_class: typing.Any, batch_size: int, **kwargs):
        self.factory_class = factory_class
        self.batch_size = batch_size
        self.kwargs = kwargs

    def load(self) -> list[dict]:
        try:
            if hasattr(self.factory_class, "build"):
                return [self.factory_class.build(**self.kwargs) for _ in range(self.batch_size)]

            return [self.factory_class(**self.kwargs) for _ in range(self.batch_size)]
        except Exception as e:
            raise SeederException(f"Failed to generate factory data: {e}") from e
