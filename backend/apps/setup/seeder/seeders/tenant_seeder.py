from apps.setup.seeder.base import BaseSeeder
from apps.setup.seeder.sources import FixtureSource
from apps.tenants.models import OrganizationTenant


class TenantSeeder(BaseSeeder):
    model = OrganizationTenant
    data_source = FixtureSource(["tenant_public.json", "tenant_ngosite.json", "tenant_restrauntsite.json"])
