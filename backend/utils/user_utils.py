from typing import TYPE_CHECKING

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django_tenants.utils import get_public_schema_name, schema_context

if TYPE_CHECKING:
    from django.contrib.auth.models import User

    from backend.apps.tenants.models import OrganizationTenant

User = get_user_model()  # noqa F811
OrganizationTenant = apps.get_model(settings.TENANT_MODEL)  # noqa F811


class PublicUserCreationError(Exception):
    pass


class PrivateUserCreation(Exception):
    pass


class UserCreationUtils:

    @staticmethod
    def is_schema_avl(schema_name: str) -> bool:
        return OrganizationTenant.objects.filter(schema_name=schema_name).exists()

    @staticmethod
    def user_creation(username: str, password: str, schema: str, create_super: bool = False) -> "User":
        """
        Create a user in current schema,
        The transaction is atomic, so if any exception occurs just rollback
        Args:
            username (str): Username of the user.
            password (str): Raw password string
            create_super (bool, optional): Create Super User
                defaults to False
        """
        if not schema:
            raise PrivateUserCreation("Schema Name is required")

        if not UserCreationUtils.is_schema_avl(schema):
            raise PrivateUserCreation("Schema not available")

        with schema_context(schema):
            with transaction.atomic():
                user = None
                if create_super:
                    user = User.objects.create_superuser(username=username, password=password)
                else:
                    user = User.objects.create_user(username=username, password=password)
                return user

    @staticmethod
    def bootstrap_users(private_creds: dict, public_creds: dict):
        """Bootstrap initial tenant users"""

        try:
            UserCreationUtils.user_creation(**public_creds)
        except Exception as e:
            raise PublicUserCreationError(str(e)) from e

        for creds in private_creds:
            try:
                UserCreationUtils.user_creation(**creds)
            except Exception as e:
                raise PrivateUserCreation(str(e)) from e

    @staticmethod
    def private_tenant_creds():
        """Private tenant creation creds
        TODO: Currently this is very unsafe and not production safe.
        This way plain text creds are always avl. in django settings
        """
        BOOTSTRAP_SCHEMA = settings.BOOTSRAP_SCHEMA_NAME
        BOOTSRAP_PASSWORD_POSTFIX = settings.DEV_PASS
        BOOTSTRAP_CREDS = [
            {
                "username": f"admin1@{BOOTSTRAP_SCHEMA}.com",
                "password": f"{BOOTSTRAP_SCHEMA}{BOOTSRAP_PASSWORD_POSTFIX}",
                "schema": BOOTSTRAP_SCHEMA,
                "create_super": True,
            },
            {
                "username": f"client1@{BOOTSTRAP_SCHEMA}.com",
                "password": f"{BOOTSTRAP_SCHEMA}{BOOTSRAP_PASSWORD_POSTFIX}",
                "schema": BOOTSTRAP_SCHEMA,
                "create_super": False,
            },
        ]
        return BOOTSTRAP_CREDS

    @staticmethod
    def public_tenant_creds(username: str = None, password: str = None, create_super: bool = True):
        """Public Tenant Creation Creds
        TODO: Currently this is very unsafe and not production safe.
        This way plain text creds are always avl. in django settings
        """

        return {
            "username": username or settings.PUBLIC_USERNAME,
            "password": password or settings.PUBLIC_PASSWORD,
            "schema": get_public_schema_name(),
            "create_super": create_super,
        }
