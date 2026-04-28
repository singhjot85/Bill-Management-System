from typing import TYPE_CHECKING

from django.apps import apps
from django.conf import settings
from django.db import transaction
from django_tenants.utils import get_public_schema_name

from .constants import TenantTypes

if TYPE_CHECKING:
    from project_apps.tenants.models import OrganizationTenant, OrganizationDomain

OrganizationTenant = apps.get_model(settings.TENANT_MODEL)
OrganizationDomain = apps.get_model(settings.TENANT_DOMAIN_MODEL)

class TenantCreationError(Exception):
    pass


class DomainCreationError(Exception):
    pass


class DomainConfig:
    """
    Responsible only for:
    - validating domain prefixes
    - resolving final full domain names
    """

    def __init__(
        self,
        domain_names: list[str] | None = None,
        is_public: bool = False,
    ):
        self.is_public = is_public
        self.domain_names = domain_names or []

        self._validate()

    @property
    def resolved_domain(self) -> str:
        """
        Example:
            DEBUG=True  -> localhost
            DEBUG=False -> example.com
        """
        if settings.DEBUG:
            return "localhost"

        return settings.RESOLVED_DOMAIN

    def _validate(self):
        """
        Validation rules:
        - Public tenant can have empty domain list
        - Private tenant must have valid subdomain names
        """

        if self.is_public:
            return

        if not self.domain_names:
            raise DomainCreationError(
                "Private tenant requires at least one domain."
            )

        for domain in self.domain_names:
            if not isinstance(domain, str):
                raise DomainCreationError(
                    f"Invalid domain: {domain}"
                )

            if not domain.strip():
                raise DomainCreationError(
                    "Empty domain name is not allowed."
                )

            if not domain.replace("-", "").isalnum():
                raise DomainCreationError(
                    f"Invalid domain name: {domain}"
                )

    def build_domains(self) -> list[str]:
        """
        Returns final domain names

        Public:
            example.com

        Private:
            org1.example.com
            org2.example.com
        """

        if self.is_public:
            return [self.resolved_domain]

        return [
            f"{domain}.{self.resolved_domain}"
            for domain in self.domain_names
        ]

class TenantCreationUtils:

    @staticmethod
    def get_attrs(model, **kwargs) -> dict:
        """Pick out class/model Attributes from passed kwargs"""
        return_kwargs = {k: v for k, v in kwargs.items() if hasattr(model, k)}
        return return_kwargs

    @staticmethod
    def create_domains(
        tenant: "OrganizationTenant",
        domain_config: DomainConfig,
    ) -> list["OrganizationDomain"]:

        created_domains = []

        for domain_name in domain_config.build_domains():
            domain, _ = OrganizationDomain.objects.get_or_create(
                tenant=tenant,
                domain=domain_name
            )
            created_domains.append(domain)

        return created_domains

    @staticmethod
    def _create_tenant(**kwargs) -> "OrganizationTenant":
        defaults = TenantCreationUtils.get_attrs(OrganizationTenant, **kwargs)
        schema_name = defaults.pop("schema_name", None)
        if schema_name:
            if not (org := OrganizationTenant.objects.filter(schema_name=schema_name).first()):
                org, _ = OrganizationTenant.objects.get_or_create(schema_name=schema_name, defaults=defaults)
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
        
        with transaction.atomic(): # If anything fails revert all db changes
            tenant = TenantCreationUtils._create_tenant(schema_name=schema_name, name=tenant_name)
            if create_domain:
                if not domain_config and schema_name != get_public_schema_name():
                    raise TenantCreationError("Domain info also needed to create a tenant.")
                domains = TenantCreationUtils.create_domains(tenant, domain_config)

        return tenant, domains
