import typing

from django.contrib.auth import get_user_model

from .base_seeder import BaseSeeder

User = get_user_model()

if typing.TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser


class UserSeeder(BaseSeeder):
    label = "User Seeder"
    REGISTERY_KEY = "auth_user"

    data_cache_key: str = "user_seeder_data"
    user_seeder_data: dict

    def run_in_schema(self):
        """Currently assume data file's are per tenant."""
        return self.seed_data.get("OrganizationTenant").get("schema_name")

    def seed(self, *args, **kwargs):
        user_data: list[dict] = self.seed_data.get("Users")
        self.create_object(User, user_data)

    def setter_password(self, model_instance: "AbstractUser", field_name: str, value: typing.Any) -> None:
        """Setter for password field for user password, to convert password into a hash we'll use set_password

        Args:
            model_instance (models.Model): Current object under execution.
            field_name (str): Name of the field.
            value (Any): Data for that field from entire data object.
        """
        if field_name == "password":
            model_instance.set_password(value)
