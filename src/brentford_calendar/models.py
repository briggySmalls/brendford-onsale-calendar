"""Data models for Brentford FC fixture ticketing."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class Link(BaseModel):
    """A link/button with metadata."""

    title: str
    url: str
    is_external: bool
    is_active: bool
    id: str
    type: str
    membership_only: bool
    season_ticket_only: bool

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class FixtureData(BaseModel):
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

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class CalendarEventData(BaseModel):
    """Data for creating/updating a Google Calendar event."""

    summary: str
    description: str
    start: datetime
    end: datetime
    source_id: str
    url: str | None = None
