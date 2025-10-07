"""Tests for ProcessedFixtureData model and category parsing."""

import json
from pathlib import Path

from brentford_calendar.models import FixtureData, ProcessedFixtureData


def test_from_fixture_data_matches_expected() -> None:
    """Test that FixtureData converts to ProcessedFixtureData as expected."""
    # Load raw fixtures
    raw_path = Path(__file__).parent / "data" / "expected-fixtures.json"
    with raw_path.open() as f:
        raw_data = json.load(f)

    # Load expected processed fixtures
    expected_path = (
        Path(__file__).parent / "data" / "expected-fixtures-categorised.json"
    )
    with expected_path.open() as f:
        expected_data = json.load(f)

    # Convert and validate
    for raw_json, expected_json in zip(raw_data, expected_data, strict=True):
        raw_fixture = FixtureData.model_validate(raw_json)
        processed = ProcessedFixtureData.from_fixture_data(raw_fixture)
        expected = ProcessedFixtureData.model_validate(expected_json)

        assert processed == expected
