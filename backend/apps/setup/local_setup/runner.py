import logging

from .constants import TENANT_DATA_FILE_NAMES
from .guards import is_local_env
from .seeders import SeederException, TenantSeeder, UserSeeder

LOGGER = logging.getLogger()


def run_local_setup():
    try:
        if not is_local_env():
            LOGGER.info("Not in development mode, so cannot run local setup.")
            return

        for file_name in TENANT_DATA_FILE_NAMES:
            TenantSeeder(file_name).run()
            UserSeeder(file_name).run()

    except SeederException as se:
        raise se
    except Exception as e:
        LOGGER.error("An unknown exception has occurred >>> ", str(e))
        raise e


def bootstrap_users():
    try:
        if not is_local_env():
            LOGGER.info("Not in development mode, so cannot run local setup.")
            return

        for file_name in TENANT_DATA_FILE_NAMES:
            UserSeeder(file_name).run()

    except SeederException as se:
        raise se
    except Exception as e:
        LOGGER.error("An unknown exception has occurred >>> ", str(e))
        raise e


def bootstrap_tenants():
    try:
        if not is_local_env():
            LOGGER.info("Not in development mode, so cannot run local setup.")
            return

        for file_name in TENANT_DATA_FILE_NAMES:
            TenantSeeder(file_name).run()

    except SeederException as se:
        raise se
    except Exception as e:
        LOGGER.error("An unknown exception has occurred >>> ", str(e))
        raise e
