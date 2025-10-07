"""Data models for Brentford FC fixture ticketing."""

import re
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelCaseAliasBaseModel(BaseModel):
    """Base model with camelCase alias generation."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class MembershipType(str, Enum):
    """Ticket membership category types."""

    SEASON_TICKET = "Season Ticket and Premium Seat Holders"
    MY_BEES_MEMBERS = "My Bees Members"
    MEMBERS = "Members"


class Link(CamelCaseAliasBaseModel):
    """A link/button with metadata."""

    title: str
    url: str
    is_external: bool
    is_active: bool
    id: str
    type: str
    membership_only: bool
    season_ticket_only: bool


class FixtureData(CamelCaseAliasBaseModel):
    """Complete fixture ticketing information from the website."""

    title: str
    opposition_name: str
    opposition_badge: str
    is_home_fixture: bool
    fixture_date: datetime
    competition: str
    category: str
    buy_now_link: Link
    find_out_more_link: Link
    sale_status: str

    # Sale windows (category 1-4)
    category1_label: str
    category1_on_sale_date: datetime
    category1_event_id: str

    category2_label: str
    category2_on_sale_date: datetime
    category2_event_id: str

    category3_label: str
    category3_on_sale_date: datetime
    category3_event_id: str

    category4_label: str
    category4_on_sale_date: datetime
    category4_event_id: str


class CalendarEventData(BaseModel):
    """Data for creating/updating a Google Calendar event."""

    summary: str
    description: str
    start: datetime
    end: datetime
    source_id: str
    url: str | None = None


class CategoryWindow(CamelCaseAliasBaseModel):
    """A ticket sale window for a specific membership category."""

    membership_type: MembershipType
    minimum_taps: int
    on_sale_date: datetime
    event_id: str


class GeneralFixtureData(CamelCaseAliasBaseModel):
    """General fixture information without category-specific data."""

    title: str
    opposition_name: str
    opposition_badge: str
    is_home_fixture: bool
    fixture_date: datetime
    competition: str
    category: str
    buy_now_link: Link
    find_out_more_link: Link


class ProcessedFixtureData(CamelCaseAliasBaseModel):
    """Fixture data with parsed category windows."""

    general_fixture_data: GeneralFixtureData
    categories: list[CategoryWindow]

    @staticmethod
    def _parse_category_label(label: str) -> tuple[MembershipType, int]:
        """Parse a category label to extract membership type and minimum TAPs.

        Args:
            label: Category label like "My Bees members with 500+ TAPs"

        Returns:
            Tuple of (membership_type, minimum_taps)
        """
        if not label:
            raise ValueError("Empty category label")

        # Extract TAPs if present (handles commas like "1,760+")
        taps_match = re.search(r"([\d,]+)\+\s*TAPS?", label, re.IGNORECASE)
        minimum_taps = 0
        if taps_match:
            # Remove commas and convert to int
            minimum_taps = int(taps_match.group(1).replace(",", ""))

        # Determine membership type
        label_lower = label.lower()

        if "my bees" in label_lower:
            membership_type = MembershipType.MY_BEES_MEMBERS
        elif "season ticket" in label_lower:
            membership_type = MembershipType.SEASON_TICKET
        elif "all members" in label_lower:
            membership_type = MembershipType.MEMBERS
        else:
            msg = f"Unknown membership type in label: {label}"
            raise ValueError(msg)

        return membership_type, minimum_taps

    @staticmethod
    def from_fixture_data(fixture: FixtureData) -> "ProcessedFixtureData":
        """Convert raw FixtureData to ProcessedFixtureData with parsed categories.

        Args:
            fixture: Raw fixture data from website

        Returns:
            ProcessedFixtureData with parsed category windows
        """
        categories = []

        # Process each of the 4 category slots
        category_slots = [
            (
                fixture.category1_label,
                fixture.category1_on_sale_date,
                fixture.category1_event_id,
            ),
            (
                fixture.category2_label,
                fixture.category2_on_sale_date,
                fixture.category2_event_id,
            ),
            (
                fixture.category3_label,
                fixture.category3_on_sale_date,
                fixture.category3_event_id,
            ),
            (
                fixture.category4_label,
                fixture.category4_on_sale_date,
                fixture.category4_event_id,
            ),
        ]

        for label, on_sale_date, event_id in category_slots:
            # Skip empty categories
            if not label or not event_id:
                continue

            membership_type, minimum_taps = ProcessedFixtureData._parse_category_label(
                label
            )

            categories.append(
                CategoryWindow(
                    membership_type=membership_type,
                    minimum_taps=minimum_taps,
                    on_sale_date=on_sale_date,
                    event_id=event_id,
                )
            )

        general_fixture_data = GeneralFixtureData(
            title=fixture.title,
            opposition_name=fixture.opposition_name,
            opposition_badge=fixture.opposition_badge,
            is_home_fixture=fixture.is_home_fixture,
            fixture_date=fixture.fixture_date,
            competition=fixture.competition,
            category=fixture.category,
            buy_now_link=fixture.buy_now_link,
            find_out_more_link=fixture.find_out_more_link,
        )

        return ProcessedFixtureData(
            general_fixture_data=general_fixture_data,
            categories=categories,
        )
