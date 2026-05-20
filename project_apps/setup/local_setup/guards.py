from typing import TYPE_CHECKING

from django.conf import settings

if TYPE_CHECKING:
    from project_apps.tenants.models import OrganizationTenant


def is_local_env() -> bool:
    return settings.DEBUG and (settings.CURRENT_ENV in settings.LOCAL_ENVS)


def is_org_in_production(org: "OrganizationTenant") -> bool:
    return org.in_production
