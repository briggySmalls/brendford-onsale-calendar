"""Tests for OnsaleFixtureData model and filtering."""

import json
from pathlib import Path

from brentford_calendar.models import (
    MembershipType,
    OnsaleFixtureData,
    ProcessedFixtureData,
)


def test_from_processed_fixture_data_matches_expected() -> None:
    """Test that ProcessedFixtureData converts to OnsaleFixtureData as expected."""
    # Load processed fixtures
    categorised_path = (
        Path(__file__).parent / "data" / "expected-fixtures-categorised.json"
    )
    with categorised_path.open() as f:
        categorised_data = json.load(f)

    # Load expected onsale filtered fixtures
    expected_path = (
        Path(__file__).parent / "data" / "expected-fixtures-onsale-filtered.json"
    )
    with expected_path.open() as f:
        expected_data = json.load(f)

    # Convert with MY_BEES_MEMBERS membership and 400 taps
    onsale_fixtures = []
    for categorised_json in categorised_data:
        processed = ProcessedFixtureData.model_validate(categorised_json)
        onsale = OnsaleFixtureData.from_processed_fixture_data(
            processed, MembershipType.MY_BEES_MEMBERS, 400
        )
        if onsale is not None:
            onsale_fixtures.append(onsale)

    # Validate against expected
    expected_fixtures = [
        OnsaleFixtureData.model_validate(item) for item in expected_data
    ]

    assert len(onsale_fixtures) == len(expected_fixtures)
    for onsale, expected in zip(onsale_fixtures, expected_fixtures, strict=True):
        assert onsale == expected
