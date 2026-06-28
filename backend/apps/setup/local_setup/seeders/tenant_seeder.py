import logging

from apps.tenants.models import OrganizationBranding, OrganizationTenant

from .base_seeder import BaseSeeder, SeederException

LOGGER = logging.getLogger()


class TenantSeeder(BaseSeeder):
    label = "Tenant Seeder"
    REGISTERY_KEY = "organization_tenants"

    data_cache_key: str = "tenant_seeder_data"
    tenant_seeder_data: dict = None

    def validate_schema(self, schema_name: str):
        """Schema doesn't exist yet, so the validation won't work"""
        return schema_name

    def seed(self, *args, **kwargs):
        org_data = self.seed_data.get(OrganizationTenant.__name__, None)

        if not org_data:
            raise SeederException(f"data not found mention it under: {OrganizationTenant.__name__}") from None

        tenant = self.create_object(OrganizationTenant, org_data)
        if not tenant:
            raise SeederException("Error creating tenant") from None

        branding_data = self.seed_data.get(OrganizationBranding.__name__)
        if not branding_data:
            LOGGER.info(f"No branding data found for >>> {tenant}, Skipping branding creation")

        self.create_object(OrganizationBranding, branding_data)
