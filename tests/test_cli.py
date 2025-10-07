"""Tests for CLI."""

import json

from click.testing import CliRunner

from brentford_calendar.cli import main


def test_cli_scrapes_and_outputs_json() -> None:
    """Test that CLI scrapes fixtures and outputs valid JSON."""
    runner = CliRunner()
    result = runner.invoke(main)

    assert result.exit_code == 0

    # Output should be valid JSON
    fixtures = json.loads(result.output)
    assert isinstance(fixtures, list)
    assert len(fixtures) > 0

    # Check first fixture has expected fields
    assert "title" in fixtures[0]
    assert "oppositionName" in fixtures[0]
    assert "fixtureDate" in fixtures[0]


def test_cli_verbose_flag() -> None:
    """Test that verbose flag is accepted."""
    runner = CliRunner()
    result = runner.invoke(main, ["-v"])
    assert result.exit_code == 0

    result = runner.invoke(main, ["-vv"])
    assert result.exit_code == 0
