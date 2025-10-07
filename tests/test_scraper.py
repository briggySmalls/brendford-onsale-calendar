"""Tests for the web scraper."""

import json
from pathlib import Path

import pytest

from brentford_calendar.scraper import extract_fixtures

# Path to test fixtures
FIXTURE_HTML_PATH = Path(__file__).parent / "data" / "ticket-information.html"
EXPECTED_FIXTURES_PATH = Path(__file__).parent / "data" / "expected-fixtures.json"


def test_extract_fixtures_from_real_html() -> None:
    """Test parsing fixtures from actual HTML fixture file.

    This test validates:
    - All fixtures are parsed correctly
    - HTML entities are properly decoded
    - Structure matches expected JSON fixture exactly
    """
    html_content = FIXTURE_HTML_PATH.read_text()
    fixtures = extract_fixtures(html_content)

    # Load expected fixtures
    expected_fixtures = json.loads(EXPECTED_FIXTURES_PATH.read_text())

    # All fixtures should match expected structure exactly
    assert fixtures == expected_fixtures


def test_extract_fixtures_from_empty_html() -> None:
    """Test that empty HTML returns empty list."""
    fixtures = extract_fixtures("<html><body></body></html>")
    assert fixtures == []


def test_extract_fixtures_handles_malformed_json() -> None:
    """Test handling of malformed JSON in data-props."""
    html = """
    <html>
        <div data-component="FixtureTicketingModule"
             data-props="not valid json"></div>
    </html>
    """

    with pytest.raises(json.JSONDecodeError):
        extract_fixtures(html)


def test_extract_fixtures_skips_divs_without_data_props() -> None:
    """Test that divs without data-props are skipped."""
    html = """
    <html>
        <div data-component="FixtureTicketingModule"></div>
        <div data-component="FixtureTicketingModule"
             data-props='{"title": "Test"}'></div>
    </html>
    """

    fixtures = extract_fixtures(html)
    assert len(fixtures) == 1
    assert fixtures[0]["title"] == "Test"
