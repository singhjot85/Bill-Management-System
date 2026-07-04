from django.apps import AppConfig


class SetupConfig(AppConfig):
    from django.conf import settings

    default_auto_field = "django.db.models.BigAutoField"
    name = settings.APP_SETUP

    def ready(self):

        self.register_seeders()

    def register_seeders(self):
        from apps.setup.local_setup.constants import seeder_registry
        from apps.setup.local_setup.seeders.configuration_seeder import ConfigSeeder
        from apps.setup.local_setup.seeders.notification_seeder import (
            NotificationSeeder,
        )
        from apps.setup.local_setup.seeders.tenant_seeder import TenantSeeder
        from apps.setup.local_setup.seeders.user_seeder import UserSeeder

        seeder_registry.register(TenantSeeder)
        seeder_registry.register(UserSeeder)
        seeder_registry.register(NotificationSeeder)
        seeder_registry.register(ConfigSeeder)
