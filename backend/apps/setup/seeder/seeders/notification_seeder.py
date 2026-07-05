from apps.notifications.models import NotificationTemplate
from apps.setup.seeder.base import BaseSeeder, Scope
from apps.setup.seeder.seeders.user_seeder import UserSeeder
from apps.setup.seeder.sources import TenantAwareFixtureSource


class NotificationSeeder(BaseSeeder):
    model = NotificationTemplate
    scope = Scope.PER_TENANT
    depends_on = [UserSeeder]
    data_source = TenantAwareFixtureSource(
        {
            "public": "tenant_public.json",
            "localngo": "tenant_ngosite.json",
            "localrestraunt": "tenant_restrauntsite.json",
        }
    )
