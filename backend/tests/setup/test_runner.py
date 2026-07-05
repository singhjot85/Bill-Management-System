from unittest.mock import MagicMock, patch

import pytest

from apps.setup.local_setup.runner import (
    bootstrap_tenants,
    bootstrap_users,
    run_local_setup,
)


@pytest.mark.skip("Bad tests, rewrite these one's all the seeders are refactored")
class TestRunner:
    """
    Unit tests for the setup runner (orchestrator).
    Ensures that the correct seeders are triggered based on the environment state.
    """

    @patch("apps.setup.local_setup.runner.is_local_env")
    @patch("apps.setup.local_setup.seeders.TenantSeeder")
    @patch("apps.setup.local_setup.seeders.UserSeeder")
    @patch("apps.setup.local_setup.seeders.NotificationSeeder")
    @patch("apps.setup.local_setup.seeders.ConfigSeeder")
    def test_run_local_setup_success(
        self,
        mock_config_seeder: MagicMock,
        mock_notification_seeder: MagicMock,
        mock_user_seeder: MagicMock,
        mock_tenant_seeder: MagicMock,
        mock_is_local: MagicMock,
    ):
        """
        Test that run_local_setup executes all registered seeders
        when the environment is identified as local.
        """
        mock_is_local.return_value = True

        run_local_setup()

        # Verify all seeders were instantiated and run() was called on their instances
        assert mock_tenant_seeder.call_count > 0
        assert mock_user_seeder.call_count > 0
        assert mock_notification_seeder.call_count > 0
        assert mock_config_seeder.call_count > 0

        mock_tenant_seeder.return_value.run.assert_called()
        mock_user_seeder.return_value.run.assert_called()
        mock_notification_seeder.return_value.run.assert_called()
        mock_config_seeder.return_value.run.assert_called()

    @patch("apps.setup.local_setup.runner.is_local_env")
    @patch("apps.setup.local_setup.seeders.TenantSeeder")
    def test_run_local_setup_not_local(self, mock_tenant_seeder: MagicMock, mock_is_local: MagicMock):
        """
        Test that run_local_setup does nothing when the environment
        is not identified as local.
        """
        mock_is_local.return_value = False

        run_local_setup()

        mock_tenant_seeder.assert_not_called()

    @patch("apps.setup.local_setup.runner.is_local_env")
    @patch("apps.setup.local_setup.seeders.UserSeeder")
    def test_bootstrap_users(self, mock_user_seeder: MagicMock, mock_is_local: MagicMock):
        """
        Test that bootstrap_users correctly triggers only the UserSeeder
        in a local environment.
        """
        mock_is_local.return_value = True

        bootstrap_users()

        mock_user_seeder.return_value.run.assert_called()

    @patch("apps.setup.local_setup.runner.is_local_env")
    @patch("apps.setup.local_setup.seeders.TenantSeeder")
    def test_bootstrap_tenants(self, mock_tenant_seeder: MagicMock, mock_is_local: MagicMock):
        """
        Test that bootstrap_tenants correctly triggers only the TenantSeeder
        in a local environment.
        """
        mock_is_local.return_value = True

        bootstrap_tenants()

        mock_tenant_seeder.return_value.run.assert_called()
