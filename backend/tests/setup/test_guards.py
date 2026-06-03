from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock

import pytest

from apps.setup.local_setup.guards import is_local_env, is_org_in_production

if TYPE_CHECKING:
    from apps.tenants.models import OrganizationTenant


class TestGuards:
    """
    Tests for environment guards and safety checks.
    Ensures that seeding and setup logic only runs in appropriate environments.
    """

    @pytest.mark.parametrize(
        "debug, current_env, local_envs, expected",
        [
            (True, "local", ["local", "dev"], True),
            (True, "dev", ["local", "dev"], True),
            (False, "local", ["local", "dev"], False),
            (True, "prod", ["local", "dev"], False),
            (False, "prod", ["local", "dev"], False),
        ],
    )
    def test_is_local_env(self, settings: Any, debug: bool, current_env: str, local_envs: list[str], expected: bool):
        """
        Test that is_local_env accurately identifies development environments
        based on Django settings.
        """
        settings.DEBUG = debug
        settings.CURRENT_ENV = current_env
        settings.LOCAL_ENVS = local_envs

        assert is_local_env() is expected

    def test_is_org_in_production(self):
        """
        Test that is_org_in_production correctly identifies the production
        status of an organization tenant.
        """
        mock_org: "OrganizationTenant" = MagicMock()

        mock_org.in_production = True
        assert is_org_in_production(mock_org) is True

        mock_org.in_production = False
        assert is_org_in_production(mock_org) is False
