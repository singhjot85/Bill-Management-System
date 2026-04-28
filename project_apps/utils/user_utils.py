from typing import TYPE_CHECKING

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django_tenants.utils import get_public_schema_name, schema_context

if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from project_apps.tenants.models import OrganizationTenant

User = get_user_model()
OrganizationTenant = apps.get_model(settings.TENANT_MODEL)

class PublicUserCreationError(Exception):
    pass

class PrivateUserCreation(Exception):
    pass

class UserCreationUtils():

    @staticmethod
    def is_schema_avl(schema_name: str) -> bool:
        return OrganizationTenant.objects.filter(schema_name=schema_name).exists()

    @staticmethod
    def _create_user(username: str, password: str):
        """
        Create a user in current schema,
        The transaction is atomic, so if any exception occurs just rollback
        Args:
            username (str): Username of the user.
            password (str): Raw password string
        """
        with transaction.atomic():
            user, _ = User.objects.get_or_create(username=username)
            if user:
                user.set_password(password)
                user.first_name = username
                user.save(update_fields=["first_name", "password"])

    @staticmethod
    def public_user_creation(username: str, password: str):
        schema = get_public_schema_name()

        if not UserCreationUtils.is_schema_avl(schema):
            raise PublicUserCreationError("Schema not available")

        with schema_context(schema):
            UserCreationUtils._create_user(username, password)
    
    @staticmethod
    def private_user_creation(username: str, password: str, schema: str):
        if not schema:
            raise PrivateUserCreation("Schema Name is required")

        if not UserCreationUtils.is_schema_avl(schema):
            raise PrivateUserCreation("Schema not available")
        
        with schema_context(schema):
            UserCreationUtils._create_user(username, password)

    @staticmethod
    def bootstrap_users():
        """Bootstrap initial tenant users"""

        username = "admin"
        raw_password = "qwerty123"
        try:
            UserCreationUtils.public_user_creation(username, raw_password)
        except Exception as e:
            raise e


        schema = settings.BOOTSRAP_SCHEMA_NAME
        username = f"admin1@{schema}.com"
        try:
            UserCreationUtils.private_user_creation(username, raw_password, schema)
        except Exception as e:
            raise e
