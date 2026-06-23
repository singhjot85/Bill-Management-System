import logging
from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model

from .base_seeder import BaseSeeder, SeederException

if TYPE_CHECKING:
    from django.contrib.auth.models import User

LOGGER = logging.getLogger()
User = get_user_model()  # noqa F811


class UserSeeder(BaseSeeder):
    label = "User Seeder"
    REGISTERY_KEY = "auth_user"
    user_seeder_data: dict = None

    def __init__(self, file_name: str):
        super().__init__()
        self.load_data(file_name, "user_seeder_data")

    def _is_existing_user(self, user_fields: dict):
        return User.objects.filter(**user_fields).exists()

    def _create_user(self, user_fields: dict, super: bool = False):
        if super:
            return User.objects.create_superuser(**user_fields)
        return User.objects.create_user(**user_fields)

    def seed(self, *args, **kwargs):
        user_data: list[dict] = self.user_seeder_data.get("Users")
        for data in user_data:
            try:
                username = data.get("username")
                LOGGER.info("Creating user >>> %s", username)
                fields = self.filter_model_fields(User, data)

                if self._is_existing_user(fields):
                    LOGGER.warning("[%s] User alredy exist, skipping creation...", username)
                    continue

                self._create_user(fields, super=data.get("create_superuser", False))
            except Exception as e:
                LOGGER.error("User creation failed >>> %s", str(e))
                raise SeederException(str(e)) from e

    def run_in_schema(self) -> str:
        if not self.user_seeder_data:
            return "public"
        return self.user_seeder_data.get("OrganizationTenant", {}).get("schema_name", "public")
