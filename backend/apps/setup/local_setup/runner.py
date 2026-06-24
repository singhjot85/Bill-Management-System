import logging

from .constants import TENANT_DATA_FILE_NAMES, seeder_registry
from .guards import is_local_env
from .seeders import (
    ConfigSeeder,
    NotificationSeeder,
    SeederException,
    TenantSeeder,
    UserSeeder,
)

LOGGER = logging.getLogger()


def run_local_setup(seeder_name: str = None):
    """Run seeders to setup current environment.

    Args:
        seeder_name (str, optional): Name of the seeder to run
            By Default all seeders run

    Raises:
        SeederException: Any Seeder Level Exceptions.
        Exception: General Exception for something unknown.
    """
    try:
        if not is_local_env():
            LOGGER.info("Not in development mode, so cannot run local setup.")
            return

        seeders = None
        if seeder_name:
            seeder_cls = seeder_registry.get(seeder_name)
            if seeder_cls:
                seeders = {seeder_name: seeder_cls}
        else:
            seeders = seeder_registry.registry

        if not seeders:
            raise SeederException("Seeders not found")

        for key, seeder_cls in seeders.items():
            resolved_seeder_cls = globals().get(seeder_cls.__name__, seeder_cls)
            label = getattr(resolved_seeder_cls, "label", key)
            LOGGER.info("[%s] Seeder Started Running...", label)

            for file_name in TENANT_DATA_FILE_NAMES:
                seeder_instance = resolved_seeder_cls(file_name)
                if not hasattr(seeder_instance, "run"):
                    raise SeederException(f"[{label}] Invalid seeder !!")
                seeder_instance.run()

    except SeederException as se:
        raise se
    except Exception as e:
        LOGGER.error("An unknown exception has occurred >>> %s", str(e))
        raise e


def bootstrap_users():
    try:
        if not is_local_env():
            LOGGER.info("Not in development mode, so cannot run local setup.")
            return

        for file_name in TENANT_DATA_FILE_NAMES:
            seeder_cls = seeder_registry.get("auth_user")
            if seeder_cls:
                resolved_seeder_cls = globals().get(seeder_cls.__name__, seeder_cls)
                resolved_seeder_cls(file_name).run()

    except SeederException as se:
        raise se
    except Exception as e:
        LOGGER.error("An unknown exception has occurred >>> %s", str(e))
        raise e


def bootstrap_tenants():
    try:
        if not is_local_env():
            LOGGER.info("Not in development mode, so cannot run local setup.")
            return

        for file_name in TENANT_DATA_FILE_NAMES:
            seeder_cls = seeder_registry.get("organization_tenants")
            if seeder_cls:
                resolved_seeder_cls = globals().get(seeder_cls.__name__, seeder_cls)
                resolved_seeder_cls(file_name).run()

    except SeederException as se:
        raise se
    except Exception as e:
        LOGGER.error("An unknown exception has occurred >>> %s", str(e))
        raise e
