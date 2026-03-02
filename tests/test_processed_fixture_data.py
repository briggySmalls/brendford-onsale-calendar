"""Tests for ProcessedFixtureData model and category parsing."""

import json
import logging
from pathlib import Path

import pytest

from brentford_calendar.models import (
    FixtureData,
    MembershipType,
    ProcessedFixtureData,
)


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


class TestParseCategoryLabel:
    """Tests for _parse_category_label static method."""

    def test_all_season_ticket_holders_and_members(self) -> None:
        label = "All season ticket holders and members (purchase 6 tickets per account)"
        membership, taps = ProcessedFixtureData._parse_category_label(label)
        assert membership == MembershipType.MEMBERS
        assert taps == 0

    def test_previous_purchasers(self) -> None:
        label = "All previous purchasers (purchase 6 tickets per account)"
        membership, taps = ProcessedFixtureData._parse_category_label(label)
        assert membership == MembershipType.MEMBERS
        assert taps == 0

    def test_unrecognised_label_defaults_to_members(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        label = "Some completely unknown label"
        with caplog.at_level(logging.WARNING):
            membership, taps = ProcessedFixtureData._parse_category_label(label)
        assert membership == MembershipType.MEMBERS
        assert taps == 0
        assert "Unrecognised category label" in caplog.text

    def test_my_bees_members_with_taps(self) -> None:
        label = "My Bees members with 500+ TAPs"
        membership, taps = ProcessedFixtureData._parse_category_label(label)
        assert membership == MembershipType.MY_BEES_MEMBERS
        assert taps == 500
