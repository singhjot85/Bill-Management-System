import logging

from .constants import TENANT_DATA_FILE_NAMES, seeder_registry
from .guards import is_local_env
from .seeders import SeederException

LOGGER = logging.getLogger(__name__)


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

        LOGGER.info("Local Setup Started...")

        seeders = None
        if seeder_name:
            seeder_cls = seeder_registry.get(seeder_name)
            if seeder_cls:
                seeders = {seeder_name: seeder_cls}
        else:
            seeders = seeder_registry.registry

        if not seeders:
            msg = "Seeders to run not found"
            LOGGER.error(f"Local Setup failed: {msg}")
            raise SeederException(msg)

        if "organization_tenants" in seeders:
            for file_name in TENANT_DATA_FILE_NAMES:
                try:
                    seeder_instance = seeders.get("organization_tenants")
                    seeder_instance(file_name).run()
                except Exception as e:
                    raise SeederException("Error creating schema's") from e

        LOGGER.info("Seeders to run >>> %s", seeders.keys())
        for key, seeder_cls in seeders.items():
            LOGGER.info("[%s] Seeder Started Running...", key)

            for file_name in TENANT_DATA_FILE_NAMES:
                seeder_instance = seeder_cls(file_name)
                if not hasattr(seeder_instance, "run"):
                    raise SeederException(f"[{key}] Invalid seeder !!")
                try:
                    seeder_instance.run()
                except Exception as ex:
                    msg = f"[{key}] Seeder failed >>> {str(ex)}"
                    LOGGER.error(msg)
                    raise SeederException(msg) from ex

            LOGGER.info("[%s] Seeder Passed Successfully...", key)
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
            user_seeder = seeder_registry.get("auth_user")
            if user_seeder:
                user_seeder(file_name).run()

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
                # resolved_seeder_cls = globals().get(seeder_cls.__name__, seeder_cls)
                seeder_cls(file_name).run()

    except SeederException as se:
        raise se
    except Exception as e:
        LOGGER.error("An unknown exception has occurred >>> %s", str(e))
        raise e
