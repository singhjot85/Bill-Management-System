from .base_seeder import BaseSeeder


class ConfigSeeder(BaseSeeder):
    label = "Configuration Seeder"
    config_seeder_data: dict = None
    REGISTERY_KEY = "configurations"

    def seed(self, *args, **kwargs):
        pass
