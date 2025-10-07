"""Tests for Pydantic data models."""

from datetime import UTC

import pytest
from pydantic import ValidationError

from brentford_calendar.models import FixtureData, Link


def test_link_model() -> None:
    """Test Link model parses and validates correctly."""
    link_data = {
        "title": "BUY NOW",
        "url": "https://example.com",
        "isExternal": True,
        "isActive": False,
        "id": "test-id",
        "type": "Standard",
        "membershipOnly": False,
        "seasonTicketOnly": False,
    }

    link = Link.model_validate(link_data)

    assert link == Link(
        title="BUY NOW",
        url="https://example.com",
        is_external=True,
        is_active=False,
        id="test-id",
        type="Standard",
        membership_only=False,
        season_ticket_only=False,
    )


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
        "buyNowLink": {
            "title": "BUY NOW",
            "url": "https://example.com/buy",
            "isExternal": True,
            "isActive": False,
            "id": "buy-id",
            "type": "Standard",
            "membershipOnly": False,
            "seasonTicketOnly": False,
        },
        "findOutMoreLink": {
            "title": "FIND OUT MORE",
            "url": "https://example.com/info",
            "isExternal": False,
            "isActive": False,
            "id": "info-id",
            "type": "Standard",
            "membershipOnly": False,
            "seasonTicketOnly": False,
        },
        "saleStatus": "Buy Now",
        "category1Label": "All Season Ticket Holders",
        "category1OnSaleDate": "2025-09-10T13:00:00Z",
        "category1EventId": "ABC123",
        "category2Label": "My Bees Members",
        "category2OnSaleDate": "2025-09-11T13:00:00Z",
        "category2EventId": "DEF456",
        "category3Label": "",
        "category3OnSaleDate": "0001-01-01T00:00:00Z",
        "category3EventId": "",
        "category4Label": "",
        "category4OnSaleDate": "0001-01-01T00:00:00Z",
        "category4EventId": "",
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
        buy_now_link=Link(
            title="BUY NOW",
            url="https://example.com/buy",
            is_external=True,
            is_active=False,
            id="buy-id",
            type="Standard",
            membership_only=False,
            season_ticket_only=False,
        ),
        find_out_more_link=Link(
            title="FIND OUT MORE",
            url="https://example.com/info",
            is_external=False,
            is_active=False,
            id="info-id",
            type="Standard",
            membership_only=False,
            season_ticket_only=False,
        ),
        sale_status="Buy Now",
        category1_label="All Season Ticket Holders",
        category1_on_sale_date=datetime(2025, 9, 10, 13, 0, 0, tzinfo=UTC),
        category1_event_id="ABC123",
        category2_label="My Bees Members",
        category2_on_sale_date=datetime(2025, 9, 11, 13, 0, 0, tzinfo=UTC),
        category2_event_id="DEF456",
        category3_label="",
        category3_on_sale_date=datetime(1, 1, 1, 0, 0, 0, tzinfo=UTC),
        category3_event_id="",
        category4_label="",
        category4_on_sale_date=datetime(1, 1, 1, 0, 0, 0, tzinfo=UTC),
        category4_event_id="",
    )


def test_fixture_data_validation_error() -> None:
    """Test that ValidationError is raised for invalid data."""
    with pytest.raises(ValidationError):
        FixtureData.model_validate({"title": "Test"})
