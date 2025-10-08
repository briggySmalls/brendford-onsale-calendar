"""Tests for CLI."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from brentford_calendar.cli import main


def test_cli_verbose_flag() -> None:
    """Test that verbose flag is accepted and syncs to calendar."""
    runner = CliRunner()

    # Create mock calendar client
    mock_client = MagicMock()
    mock_client.upsert_event.return_value = True

    with runner.isolated_filesystem():
        # Create dummy credentials file
        creds_path = Path("service-account.json")
        creds_path.write_text('{"type": "service_account"}')

        # Mock the config loading and client creation
        with (
            patch("brentford_calendar.cli.load_config_from_file"),
            patch(
                "brentford_calendar.cli.CalendarClient.from_config",
                return_value=mock_client,
            ),
        ):
            # Test -v flag
            result = runner.invoke(
                main,
                [
                    "-v",
                    "--membership",
                    "MY_BEES_MEMBERS",
                    "--credentials",
                    str(creds_path),
                    "--calendar-id",
                    "test@group.calendar.google.com",
                ],
            )
            assert result.exit_code == 0

            # Test -vv flag
            result = runner.invoke(
                main,
                [
                    "-vv",
                    "--membership",
                    "MY_BEES_MEMBERS",
                    "--credentials",
                    str(creds_path),
                    "--calendar-id",
                    "test@group.calendar.google.com",
                ],
            )
            assert result.exit_code == 0


def test_cli_calendar_sync() -> None:
    """Test that CLI syncs to calendar when credentials are provided."""
    runner = CliRunner()

    # Create mock calendar client
    mock_client = MagicMock()
    mock_client.upsert_event.return_value = True  # All created for simplicity

    with runner.isolated_filesystem():
        # Create dummy credentials file
        creds_path = Path("service-account.json")
        creds_path.write_text('{"type": "service_account"}')

        # Mock the config loading and client creation
        with (
            patch("brentford_calendar.cli.load_config_from_file") as mock_load_config,
            patch(
                "brentford_calendar.cli.CalendarClient.from_config",
                return_value=mock_client,
            ),
        ):
            result = runner.invoke(
                main,
                [
                    "--membership",
                    "MY_BEES_MEMBERS",
                    "--credentials",
                    str(creds_path),
                    "--calendar-id",
                    "test-calendar@group.calendar.google.com",
                ],
            )

            assert result.exit_code == 0

            # Verify config was loaded
            mock_load_config.assert_called_once()

            # Verify events were synced (at least one)
            assert mock_client.upsert_event.call_count >= 1

            # Check output message contains expected format
            assert "Synced" in result.output
            assert "events" in result.output
