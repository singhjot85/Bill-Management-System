from typing import TYPE_CHECKING

from django.conf import settings
from django_tenants.utils import get_public_schema_name
from django.apps import apps

from .constants import TenantTypes

if TYPE_CHECKING:
    from project_apps.tenants.models import OrganizationTenant, OrganizationDomain

OrganizationTenant = apps.get_model(settings.TENANT_MODEL)
OrganizationDomain = apps.get_model(settings.TENANT_DOMAIN_MODEL)

class TenantCreationError(Exception):
    pass


class DomainCreationError(Exception):
    pass


class TenantDeletionError(Exception):
    pass


class DomainDeletionError(Exception):
    pass


class DomainConfig:

    def __init__(self, domain_names: list[str], is_public: bool= False):
        """
        Args:
            domain_names (list[str]): List of strings containing domain names to be created
            is_public (bool): Is it a public tenant.
                defaults to False.
        """
        # if not (clean_domain_names := self.clean_domain_names(domain_names)):
        #     raise DomainDeletionError("Please pass the list of domains to be created")

        self._domain_names = self.clean_domain_names(domain_names)
        self._is_public = is_public

    @property
    def resolved_domain(self):
        """Resolved domain name for current app setting"""
        if hasattr(self, "_resolved_domain"):
            return self._resolved_domain
        return self._get_resolved_domain()

    def _get_resolved_domain(self):
        """Resolved domain for current app execution."""
        if settings.DEBUG:
            self._resolved_domain = "localhost"
        else:
            self._resolved_domain = settings.RESOLVED_DOMAIN
        return self._resolved_domain

    def clean_domain_names(self, domain_names: list[str]) -> list[str]:
        cleaned: list[str] = []
        for domain_name in domain_names:
            if (
                not isinstance(domain_name, str) 
                or (
                    not domain_name.isalnum()
                    or self._is_public
                )
            ):
                raise DomainCreationError(f"Domain name [{domain_name}] is not allowed.")
            cleaned.append(domain_name)
        return cleaned

    def get_domain_names(self) -> list[str]:
        """Returns list of domain names to be used for the app."""
        resolved_names = []
        for domain_name in self._domain_names:
            resolved_names.append(f"{domain_name}.{self.resolved_domain}")

    def set_tenant(self, tenant: "OrganizationTenant"):
        self._tenant = tenant

    def get_domain_data(self) -> list[dict] | list:
        data = []
        is_primary = False
        for domain_name in self.get_domain_names():
            config = {
                "tenant": self._tenant,
                "is_primary": is_primary,
            }
            config["domain"] = domain_name
            is_primary = False
            data.append(config)

        return data


class TenantCreationUtils:

    @staticmethod
    def get_attrs(model, **kwargs) -> dict:
        """Pick out class/model Attributes from passed kwargs"""
        return_kwargs = {k: v for k, v in kwargs.items() if hasattr(model, k)}
        return return_kwargs

    @staticmethod
    def _create_domain(tenant: "OrganizationTenant", *args, **kwargs) -> "OrganizationDomain":
        try:
            defaults: dict = TenantCreationUtils.get_attrs(OrganizationDomain, **kwargs)
            tenant = defaults.pop("tenant", None)
            if tenant:
                return OrganizationDomain.objects.get_or_create(tenant=tenant, defaults=defaults)
            else:
                raise DomainCreationError("Tenant not passed for domain creation.")
        except Exception as e:
            raise DomainCreationError(f"Error Creating Domain for tenant: [{kwargs.get("tenant")}]") from e

    @staticmethod
    def create_domains(tenant: "OrganizationTenant", domain_config: DomainConfig) -> list["OrganizationDomain"]:
        """
        Create a list of domains for the given tenant
        Args:
            tenant (OrganizationTenant): Tennat to be created
            domain_config (DomainConfig): List of domain strings.
        Raises:
            DomainCreationError
        """
        domain_config.set_tenant(tenant)
        domain_settings = domain_config.get_domain_data()
        domains = []
        for settings in domain_settings:
            domains.append(TenantCreationUtils._create_domain(**settings))
        return domains

    @staticmethod
    def _create_tenant(**kwargs) -> "OrganizationTenant":
        defaults = TenantCreationUtils.get_attrs(OrganizationTenant, **kwargs)
        schema_name = defaults.pop("schema_name", None)
        if schema_name:
            if not (org := OrganizationTenant.objects.filter(schema_name=schema_name)):
                org = OrganizationTenant.objects.get_or_create(schema_name=schema_name, defaults=defaults)
            return org
        raise TenantCreationError("Error occurred Creating tenant, did you provide a schema_name ??")

    @staticmethod
    def create_tenant(
        tenant_type: str, 
        schema_name: str, 
        tenant_name: str = None,
        create_domain: bool = False,
        domain_config: DomainConfig = None
    ) -> tuple["OrganizationTenant", list["OrganizationDomain"]]:
        """
        Entrypoint util for Tenant creation,
            - Creates a Organization record if not available.
            - Creates a Domain even if one exists on the org
                Intentional so that we can use this to add domains also
        Args:
            tenant_type (str): Type of tenant to be created
                constants in TenantTypes
            schema_name (str): Name of the schema.
                In PRIVATE Tenant creation it'll falback to the one in project settings.
            create_domain (bool, optional): Do we need to create domains.
                defaults to False
            domain_config (DomainConfig, optional): Domain Configuration object.
                defaults to None
            tenant_name (str, optional): Name of the tenant
        """
        if not tenant_type:
            raise TenantCreationError("Please define the type of tenant you want to create")

        if not tenant_name:
            tenant_name = schema_name.title()

        if tenant_type == TenantTypes.PUBLIC.value:
            schema_name = get_public_schema_name()

        tenant, domains = (None, [])
        tenant = TenantCreationUtils._create_tenant(schema_name=schema_name, name=tenant_name)
        if create_domain:
            if not domain_config:
                raise TenantCreationError("Domain info also needed to create a tenant.")
            domains = TenantCreationUtils.create_domains(tenant, domain_config)

        return tenant, domains
