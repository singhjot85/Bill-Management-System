from apps.setup.local_setup.constants import seeder_registry

from .base_seeder import SeederException  # noqa: F401
from .config_seeder import ConfigSeeder  # noqa: F401
from .notification_seeder import NotificationSeeder  # noqa: F401
from .tenant_seeder import TenantSeeder  # noqa: F401
from .user_seeder import UserSeeder  # noqa: F401

seeder_registry.register(TenantSeeder)
seeder_registry.register(UserSeeder)
seeder_registry.register(NotificationSeeder)
seeder_registry.register(ConfigSeeder)
