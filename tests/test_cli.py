"""Tests for CLI."""

from click.testing import CliRunner

from brentford_calendar.cli import main


def test_cli_runs_successfully() -> None:
    """Test that CLI runs and exits successfully."""
    runner = CliRunner()
    result = runner.invoke(main)
    assert result.exit_code == 0
    assert "Brentford Calendar Sync" in result.output


def test_cli_verbose_flag() -> None:
    """Test that verbose flag is accepted."""
    runner = CliRunner()
    result = runner.invoke(main, ["-v"])
    assert result.exit_code == 0

    result = runner.invoke(main, ["-vv"])
    assert result.exit_code == 0
