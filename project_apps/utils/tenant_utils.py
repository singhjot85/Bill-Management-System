from django.conf import settings
from django_tenants.utils import get_public_schema_name
from django.apps import apps

# from project_apps.tenants.models import OrganizationTenant, OrganizationDomain

OrganizationTenant = apps.get_model(settings.TENANT_MODEL)
OrganizationDomain = apps.get_model(settings.TENANT_DOMAIN_MODEL)


LOCAL_SCHEMA_NAME = "localclient"
LOCAL_TENANT_DOMAINS = [
    f"{LOCAL_SCHEMA_NAME}.localhost",
]


class TenantCreationError(Exception):
    pass


class DomainCreationError(Exception):
    pass


class TenantDeletionError(Exception):
    pass


class DomainDeletionError(Exception):
    pass


def create_domains(tenant: "OrganizationTenant", domains: list):
    if not isinstance(domains, list):
        raise ValueError("domains must be a list")

    try:
        is_primary = True

        for domain in domains:
            defaults = {
                "domain": domain,
                "is_primary": is_primary,
            }

            OrganizationDomain.objects.get_or_create(
                tenant=tenant,
                domain=domain,
                defaults=defaults,
            )

            is_primary = False

    except Exception as exc:
        raise DomainCreationError("Domain creation failed") from exc


def create_public_tenant():
    defaults = {
        "name": get_public_schema_name().title(),
    }

    try:
        org, _ = OrganizationTenant.objects.get_or_create(
            schema_name=get_public_schema_name(),
            defaults=defaults,
        )

        create_domains(org, ["localhost"])

    except Exception as exc:
        raise TenantCreationError("Public tenant creation failed") from exc


def create_local_tenant():
    defaults = {
        "name": LOCAL_SCHEMA_NAME.title(),
    }

    try:
        org, _ = OrganizationTenant.objects.get_or_create(
            schema_name=LOCAL_SCHEMA_NAME,
            defaults=defaults,
        )

        create_domains(org, LOCAL_TENANT_DOMAINS)

    except Exception as exc:
        raise TenantCreationError("Local tenant creation failed") from exc


def init_tenants():
    create_public_tenant()

    if settings.DEBUG:
        create_local_tenant()


# -----------------------------
# Reverse migration utilities
# -----------------------------


def delete_domains(tenant: "OrganizationTenant"):
    try:
        OrganizationDomain.objects.filter(
            tenant=tenant
        ).delete()

    except Exception as exc:
        raise DomainDeletionError("Domain deletion failed") from exc


def delete_public_tenant():
    try:
        tenant = OrganizationTenant.objects.filter(
            schema_name=get_public_schema_name()
        ).first()

        if not tenant:
            return

        delete_domains(tenant)

        # usually public tenant should not be deleted physically
        # but since this is for reverse migration utility:
        tenant.delete()

    except Exception as exc:
        raise TenantDeletionError("Public tenant deletion failed") from exc


def delete_local_tenant():
    try:
        tenant = OrganizationTenant.objects.filter(
            schema_name=LOCAL_SCHEMA_NAME
        ).first()

        if not tenant:
            return

        delete_domains(tenant)
        tenant.delete()

    except Exception as exc:
        raise TenantDeletionError("Local tenant deletion failed") from exc


def reverse_init_tenants():
    """
    Reverse function for RunPython migration.
    Reverse order matters:
    local tenant first -> public tenant second
    """

    if settings.DEBUG:
        delete_local_tenant()

    delete_public_tenant()