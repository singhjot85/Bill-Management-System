from django.contrib.auth import get_user_model

from .base_seeder import BaseSeeder

User = get_user_model()  # noqa F811


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
