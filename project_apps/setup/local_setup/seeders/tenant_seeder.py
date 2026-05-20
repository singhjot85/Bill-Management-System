import logging

from project_apps.tenants.models import (
    OrganizationBranding,
    OrganizationDomain,
    OrganizationTenant,
)

from .base_seeder import BaseSeeder

LOGGER = logging.getLogger()


class TenantSeeder(BaseSeeder):
    label = "Tenant Seeder"
    tenant_seeder_data: dict = None

    def __init__(self, data_file_name: str):
        super().__init__()

        self.data_file_name = data_file_name
        self.load_data(data_file_name, "tenant_seeder_data")

    def _create_tenant(self):
        try:
            tenant_data: dict = self.tenant_seeder_data.get("OrganizationTenant")
            filtered_fields = self.filter_model_fields(OrganizationTenant, tenant_data)
            tenant = OrganizationTenant(**filtered_fields)

            LOGGER.info("Created tenant >>> %s", tenant)
        except Exception as e:
            LOGGER.error("Error creating tenant >>> %s", str(e))

        return tenant

    def _create_domains(self, tenant: OrganizationTenant):
        domain_data: list[dict] = self.tenant_seeder_data.get("OrganizationDomain")
        for data in domain_data:
            try:
                filtered_fields = self.filter_model_fields(OrganizationDomain, data)
                domain = OrganizationDomain(**filtered_fields, tenant=tenant)
                # domain.tenant = tenant
                # domain.save(update_fields=["tenant"])

                LOGGER.info("[%s] Created domain >>> %s", tenant, domain)
            except Exception as e:
                LOGGER.error("[%s] Error Creating domain >>> %s", tenant, str(e))

    def _create_branding(self, tenant: OrganizationTenant):
        try:
            branding_data: dict = self.tenant_seeder_data.get("OrganizationBranding")
            filtered_fields = self.filter_model_fields(OrganizationBranding, branding_data)
            branding = OrganizationBranding(**filtered_fields, organization=tenant)
            # branding.organization = tenant
            # branding.save(update_fields=["organization"])

            LOGGER.info("[%s] Created branding >>> %s", tenant, branding)
        except Exception as e:
            LOGGER.error("[%s] Error Creating branding >>> %s", tenant, str(e))

    def seed(self, *args, **kwargs):
        tenant = self._create_tenant()
        self._create_domains(tenant)
        self._create_branding(tenant)

        return tenant
