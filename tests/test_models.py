"""Tests for Pydantic data models."""

from datetime import UTC

import pytest
from pydantic import ValidationError

from brentford_calendar.models import FixtureData, SaleWindow


def test_fixture_data_model() -> None:
    """Test FixtureData model parses and validates correctly."""
    from datetime import datetime

    fixture_dict = {
        "title": "West Ham (A)",
        "oppositionName": "West Ham United",
        "oppositionBadge": "https://example.com/badge.png",
        "isHomeFixture": False,
        "fixtureDate": "2025-10-20T20:00:00",
        "competition": "Premier League",
        "category": "Category A",
        "buyNowUrl": "https://example.com/buy",
        "findOutMoreUrl": "https://example.com/info",
        "windows": [
            {
                "label": "All Season Ticket Holders",
                "onSaleDate": "2025-09-10T13:00:00Z",
                "eventId": "ABC123",
            },
            {
                "label": "My Bees Members",
                "onSaleDate": "2025-09-11T13:00:00Z",
                "eventId": "DEF456",
            },
        ],
    }

    fixture = FixtureData.model_validate(fixture_dict)

    assert fixture == FixtureData(
        title="West Ham (A)",
        opposition_name="West Ham United",
        opposition_badge="https://example.com/badge.png",
        is_home_fixture=False,
        fixture_date=datetime(2025, 10, 20, 20, 0, 0),
        competition="Premier League",
        category="Category A",
        buy_now_url="https://example.com/buy",
        find_out_more_url="https://example.com/info",
        windows=[
            SaleWindow(
                label="All Season Ticket Holders",
                on_sale_date=datetime(2025, 9, 10, 13, 0, 0, tzinfo=UTC),
                event_id="ABC123",
            ),
            SaleWindow(
                label="My Bees Members",
                on_sale_date=datetime(2025, 9, 11, 13, 0, 0, tzinfo=UTC),
                event_id="DEF456",
            ),
        ],
    )


def test_fixture_data_validation_error() -> None:
    """Test that ValidationError is raised for invalid data."""
    with pytest.raises(ValidationError):
        FixtureData.model_validate({"title": "Test"})
