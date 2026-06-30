from apps.setup.models import Configurations
from apps.setup.seeder.base import BaseSeeder, Scope
from apps.setup.seeder.seeders.tenant_seeder import TenantSeeder
from apps.setup.seeder.sources import TenantAwareFixtureSource


class ConfigSeeder(BaseSeeder):
    model = Configurations
    scope = Scope.PER_TENANT
    depends_on = [TenantSeeder]
    data_source = TenantAwareFixtureSource(
        {
            "public": "tenant_public.json",
            "localngo": "tenant_ngosite.json",
            "localrestraunt": "tenant_restrauntsite.json",
        }
    )