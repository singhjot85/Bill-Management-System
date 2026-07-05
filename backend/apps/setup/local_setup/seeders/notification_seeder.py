import typing

from apps.notifications.models import NotificationTemplate

from ..constants import seeder_registry
from .base_seeder import BaseSeeder


class NotificationSeeder(BaseSeeder):
    label = "Notification Seeder"
    REGISTERY_KEY = "notifications"

    data_cache_key = "notification_seeder_data"
    notification_seeder_data: dict = None

    def run_in_schema(self) -> str:
        if not self.notification_seeder_data:
            return "public"
        return self.notification_seeder_data.get("OrganizationTenant", {}).get("schema_name", "public")

    def seed(self, *args, **kwargs):
        notification_data = self.seed_data.get("NotificationTemplate")
        if notification_data:
            self.create_object(NotificationTemplate, notification_data)

    def setter_plain_text(self, model_instance: "NotificationTemplate", field_name: str, value: typing.Any) -> None:
        """Setter for file fields

        Args:
            model_instance (NotificationTemplate): Current object under execution.
            field_name (str): Name of the field.
            value (Any): Data for that field from entire data object.
        """
        file_path: str = value
        content = self.load_file(file_path)
        setattr(model_instance, field_name, content)

    def setter_html(self, model_instance: "NotificationTemplate", field_name: str, value: typing.Any) -> None:
        """Setter for file fields

        Args:
            model_instance (NotificationTemplate): Current object under execution.
            field_name (str): Name of the field.
            value (Any): Data for that field from entire data object.
        """
        file_path: str = value
        content = self.load_file(file_path, file_type="html")
        setattr(model_instance, field_name, content)

    def setter_subject(self, model_instance: "NotificationTemplate", field_name: str, value: typing.Any) -> None:
        """Setter for file fields

        Args:
            model_instance (NotificationTemplate): Current object under execution.
            field_name (str): Name of the field.
            value (Any): Data for that field from entire data object.
        """
        file_path: str = value
        content = self.load_file(file_path)
        setattr(model_instance, field_name, content)


seeder_registry.register(NotificationSeeder)
