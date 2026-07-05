import typing

from apps.setup.models import Configurations

from .base_seeder import BaseSeeder


class ConfigSeeder(BaseSeeder):
    label = "Configuration Seeder"
    REGISTERY_KEY = "configurations"

    data_cache_key = "configuration_seeder_data"
    configuration_seeder_data: dict = None

    def run_in_schema(self) -> str:
        if not self.seed_data:
            return super().run_in_schema()
        return self.seed_data.get("OrganizationTenant", {}).get("schema_name", "public")

    def seed(self, *args, **kwargs):
        config_data = self.seed_data.get("Configurations")
        if config_data:
            self.create_object(Configurations, config_data)

    def setter_details(self, model_instance: "Configurations", field_name: str, value: typing.Any) -> None:
        """Setter for file fields

        Args:
            model_instance (NotificationTemplate): Current object under execution.
            field_name (str): Name of the field.
            value (Any): Data for that field from entire data object.
        """
        file_path: str = value
        content = self.load_file(file_path, file_type="json")
        setattr(model_instance, field_name, content)
