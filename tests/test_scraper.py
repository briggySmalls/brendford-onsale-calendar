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
    - Pydantic validation passes
    """
    html_content = FIXTURE_HTML_PATH.read_text()
    fixtures = extract_fixtures(html_content)

    # Should return FixtureData objects
    assert len(fixtures) >= 5

    # Convert to dicts for comparison with expected JSON
    fixtures_dict = [f.model_dump(by_alias=True, mode="json") for f in fixtures]

    # Load expected fixtures
    expected_fixtures = json.loads(EXPECTED_FIXTURES_PATH.read_text())

    # All fixtures should match expected structure exactly
    assert fixtures_dict == expected_fixtures


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
    # Use a minimal but valid fixture structure
    valid_fixture = json.dumps(
        {
            "title": "Test",
            "oppositionName": "Test FC",
            "oppositionBadge": "http://test.com/badge.png",
            "isHomeFixture": True,
            "fixtureDate": "2025-01-01T15:00:00",
            "competition": "Test League",
            "category": "Category A",
            "buyNowLink": {
                "title": "BUY",
                "url": "http://test.com",
                "isExternal": True,
                "isActive": False,
                "id": "test-id",
                "type": "Standard",
                "membershipOnly": False,
                "seasonTicketOnly": False,
            },
            "findOutMoreLink": {
                "title": "INFO",
                "url": "http://test.com/info",
                "isExternal": False,
                "isActive": False,
                "id": "test-id-2",
                "type": "Standard",
                "membershipOnly": False,
                "seasonTicketOnly": False,
            },
            "saleStatus": "Buy Now",
            "category1Label": "Test",
            "category1OnSaleDate": "2025-01-01T10:00:00+00:00",
            "category1EventId": "test1",
            "category2Label": "",
            "category2OnSaleDate": "0001-01-01T00:00:00+00:00",
            "category2EventId": "",
            "category3Label": "",
            "category3OnSaleDate": "0001-01-01T00:00:00+00:00",
            "category3EventId": "",
            "category4Label": "",
            "category4OnSaleDate": "0001-01-01T00:00:00+00:00",
            "category4EventId": "",
        }
    )

    html = f"""
    <html>
        <div data-component="FixtureTicketingModule"></div>
        <div data-component="FixtureTicketingModule"
             data-props='{valid_fixture}'></div>
    </html>
    """

    fixtures = extract_fixtures(html)
    assert len(fixtures) == 1
    assert fixtures[0].title == "Test"
