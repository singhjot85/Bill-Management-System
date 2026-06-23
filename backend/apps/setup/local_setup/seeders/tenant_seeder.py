import logging

from apps.tenants.models import (
    OrganizationBranding,
    OrganizationDomain,
    OrganizationTenant,
)

from .base_seeder import BaseSeeder

LOGGER = logging.getLogger()


class TenantSeeder(BaseSeeder):
    label = "Tenant Seeder"
    tenant_seeder_data: dict = None
    REGISTERY_KEY = "organization_tenants"

    def __init__(self, data_file_name: str):
        super().__init__()

        self.data_file_name = data_file_name
        self.load_data(data_file_name, "tenant_seeder_data")

    def _create_tenant(self):
        tenant = None
        try:
            tenant_data: dict = self.tenant_seeder_data.get("OrganizationTenant")
            filtered_fields = self.filter_model_fields(OrganizationTenant, tenant_data)
            tenant, created = OrganizationTenant.objects.get_or_create(**filtered_fields)

            if created:
                LOGGER.info("Created tenant >>> %s", tenant)
            else:
                LOGGER.info("Skipping creation tenant already exist >>> %s", tenant)
        except Exception as e:
            LOGGER.error("Error creating tenant >>> %s", str(e))

        return tenant

    def _create_domains(self, tenant: OrganizationTenant):
        domain_data: list[dict] = self.tenant_seeder_data.get("OrganizationDomain")
        for data in domain_data:
            try:
                filtered_fields = self.filter_model_fields(OrganizationDomain, data)
                domain, created = OrganizationDomain.objects.get_or_create(**filtered_fields, tenant=tenant)

                if created:
                    LOGGER.info("[%s] Created domain >>> %s", tenant, domain)
                else:
                    LOGGER.info("[%s] Skipping Creation domain already exist >>> %s", tenant, domain)
            except Exception as e:
                LOGGER.error("[%s] Error Creating domain >>> %s", tenant, str(e))

    def _create_branding(self, tenant: OrganizationTenant):
        try:
            branding_data: dict = self.tenant_seeder_data.get("OrganizationBranding")
            filtered_fields = self.filter_model_fields(OrganizationBranding, branding_data)
            branding, created = OrganizationBranding.objects.get_or_create(**filtered_fields, organization=tenant)
            # branding.organization = tenant
            # branding.save(update_fields=["organization"])

            if created:
                LOGGER.info("[%s] Created branding >>> %s", tenant, branding)
            else:
                LOGGER.info("[%s] Skipping Creation branding already exist >>> %s", tenant, branding)
        except Exception as e:
            LOGGER.error("[%s] Error Creating branding >>> %s", tenant, str(e))

    def seed(self, *args, **kwargs):
        tenant = self._create_tenant()
        if tenant:
            self._create_domains(tenant)
            self._create_branding(tenant)

        return tenant
