"""Data models for Brentford FC fixture ticketing."""

import logging
import re
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

logger = logging.getLogger(__name__)


class CamelCaseAliasBaseModel(BaseModel):
    """Base model with camelCase alias generation."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class MembershipType(str, Enum):
    """Ticket membership category types."""

    SEASON_TICKET = "Season Ticket and Premium Seat Holders"
    MY_BEES_MEMBERS = "My Bees Members"
    MEMBERS = "Members"

    def can_purchase(self, category_type: "MembershipType") -> bool:
        """Check if this membership tier can purchase tickets from a category.

        Higher tiers can purchase from equal or lower tier categories.
        Hierarchy: SEASON_TICKET > MY_BEES_MEMBERS > MEMBERS

        Args:
            category_type: The membership type required for the category

        Returns:
            True if this membership can purchase from that category
        """
        hierarchy = {
            MembershipType.SEASON_TICKET: 3,
            MembershipType.MY_BEES_MEMBERS: 2,
            MembershipType.MEMBERS: 1,
        }
        return hierarchy[self] >= hierarchy[category_type]


class SaleWindow(CamelCaseAliasBaseModel):
    """A raw on-sale window for a fixture, as listed on the website."""

    label: str
    on_sale_date: datetime
    event_id: str


class FixtureData(CamelCaseAliasBaseModel):
    """Complete fixture ticketing information from the website."""

    title: str
    opposition_name: str
    opposition_badge: str
    is_home_fixture: bool
    fixture_date: datetime
    competition: str
    category: str
    buy_now_url: str | None = None
    find_out_more_url: str

    windows: list[SaleWindow]


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
    buy_now_url: str | None
    find_out_more_url: str


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
        elif "members" in label_lower:
            membership_type = MembershipType.MEMBERS
        elif "season ticket" in label_lower:
            membership_type = MembershipType.SEASON_TICKET
        elif "previous purchaser" in label_lower:
            membership_type = MembershipType.MEMBERS
        else:
            logger.warning(
                "Unrecognised category label %r, defaulting to MEMBERS", label
            )
            membership_type = MembershipType.MEMBERS

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

        for window in fixture.windows:
            membership_type, minimum_taps = ProcessedFixtureData._parse_category_label(
                window.label
            )

            categories.append(
                CategoryWindow(
                    membership_type=membership_type,
                    minimum_taps=minimum_taps,
                    on_sale_date=window.on_sale_date,
                    event_id=window.event_id,
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
            buy_now_url=fixture.buy_now_url,
            find_out_more_url=fixture.find_out_more_url,
        )

        return ProcessedFixtureData(
            general_fixture_data=general_fixture_data,
            categories=categories,
        )


class OnsaleFixtureData(CamelCaseAliasBaseModel):
    """Fixture with single matching on-sale category for user's membership."""

    general_fixture_data: GeneralFixtureData
    onsale: CategoryWindow | None

    @staticmethod
    def from_processed_fixture_data(
        processed: ProcessedFixtureData,
        membership: MembershipType,
        taps: int,
    ) -> "OnsaleFixtureData | None":
        """Convert ProcessedFixtureData to OnsaleFixtureData for user's membership.

        Finds the first eligible category (chronologically by on-sale date) where:
        - User's membership tier can purchase the category
        - User has sufficient TAPs

        Args:
            processed: Processed fixture data with all categories
            membership: User's membership type
            taps: User's TAP count

        Returns:
            OnsaleFixtureData if any eligible categories exist, None otherwise
        """
        # Filter categories by membership eligibility and TAPs requirement
        eligible_categories = [
            cat
            for cat in processed.categories
            if membership.can_purchase(cat.membership_type) and taps >= cat.minimum_taps
        ]

        # No eligible categories means this fixture is not available
        if not eligible_categories:
            return None

        # Sort by on_sale_date to find earliest eligible category
        eligible_categories.sort(key=lambda cat: cat.on_sale_date)

        return OnsaleFixtureData(
            general_fixture_data=processed.general_fixture_data,
            onsale=eligible_categories[0],
        )

    def to_calendar_event_data(self) -> CalendarEventData:
        """Convert to Google Calendar event data.

        Returns:
            CalendarEventData for creating/updating calendar events

        Raises:
            ValueError: If onsale category is None
        """
        if self.onsale is None:
            msg = "Cannot create calendar event for fixture with no onsale category"
            raise ValueError(msg)

        # Determine fixture location (H/A)
        fixture_location = "H" if self.general_fixture_data.is_home_fixture else "A"

        # Build summary: "West Ham (A) - Tickets On Sale"
        opposition = self.general_fixture_data.opposition_name
        summary = f"{opposition} ({fixture_location}) - Tickets On Sale"

        # Build description with fixture details
        fixture_date_str = self.general_fixture_data.fixture_date.strftime(
            "%Y-%m-%d %H:%M"
        )
        # Build match teams string
        if self.general_fixture_data.is_home_fixture:
            match_str = f"Match: Brentford vs {opposition}"
        else:
            match_str = f"Match: {opposition} vs Brentford"

        description_lines = [
            match_str,
            f"Date: {fixture_date_str}",
            f"Competition: {self.general_fixture_data.competition}",
            "",
            f"Membership: {self.onsale.membership_type.value}",
            f"Minimum TAPs: {self.onsale.minimum_taps}",
        ]

        if self.general_fixture_data.buy_now_url is not None:
            description_lines.append("")
            description_lines.append(
                f"Buy tickets: {self.general_fixture_data.buy_now_url}"
            )

        description = "\n".join(description_lines)

        # Use onsale date as event start time
        from datetime import timedelta

        start_time = self.onsale.on_sale_date
        end_time = start_time + timedelta(hours=1)

        return CalendarEventData(
            summary=summary,
            description=description,
            start=start_time,
            end=end_time,
            source_id=self.onsale.event_id,
            url=self.general_fixture_data.buy_now_url,
        )
