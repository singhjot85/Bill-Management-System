from .base_seeder import BaseSeeder


class ConfigSeeder(BaseSeeder):
    label = "Configuration Seeder"
    config_seeder_data: dict = None

    def seed(self, *args, **kwargs):
        pass

    def get_tenant_schema(self, *args, **kwargs):
        return self.config_seeder_data.get("OrganizationTenant").get("schema_name")
