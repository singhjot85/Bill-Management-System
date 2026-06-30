from django.contrib.auth import get_user_model

from apps.setup.seeder.base import BaseSeeder, Scope
from apps.setup.seeder.seeders.tenant_seeder import TenantSeeder
from apps.setup.seeder.sources import TenantAwareFixtureSource


class UserSeeder(BaseSeeder):
    model = get_user_model()
    scope = Scope.PER_TENANT
    depends_on = [TenantSeeder]
    data_source = TenantAwareFixtureSource(
        {
            "public": "tenant_public.json",
            "localngo": "tenant_ngosite.json",
            "localrestraunt": "tenant_restrauntsite.json",
        }
    )
