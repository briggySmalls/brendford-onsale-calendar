"""Tests for Google Calendar client."""

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

import pytest

from brentford_calendar.calendar_client import CalendarClient
from brentford_calendar.models import CalendarEventData


@pytest.fixture
def mock_service() -> MagicMock:
    """Create a mock Google Calendar service."""
    return MagicMock()


@pytest.fixture
def calendar_client(mock_service: MagicMock) -> CalendarClient:
    """Create a CalendarClient with mocked service."""
    return CalendarClient(
        calendar_id="test-calendar@example.com",
        service=mock_service,
    )


def test_calendar_client_init(
    calendar_client: CalendarClient, mock_service: MagicMock
) -> None:
    """Test CalendarClient initialization."""
    assert calendar_client.calendar_id == "test-calendar@example.com"
    assert calendar_client.service is mock_service


def test_upsert_event_creates_new(calendar_client: CalendarClient) -> None:
    """Test upsert creates a new event when none exists."""
    start_time = datetime(2025, 9, 10, 13, 0, 0, tzinfo=UTC)
    event_data = CalendarEventData(
        summary="Test Event",
        description="Test Description",
        start=start_time,
        end=start_time + timedelta(hours=1),
        source_id="test-source-123",
        url="https://example.com/tickets",
    )

    # Mock: no existing event
    calendar_client.service.events().list().execute.return_value = {"items": []}

    # Mock: create returns new event
    mock_created_event = {"id": "new-event-123", "summary": "Test Event"}
    calendar_client.service.events().insert().execute.return_value = mock_created_event

    created = calendar_client.upsert_event(event_data)

    assert created is True

    # Verify insert was called
    call_args = calendar_client.service.events().insert.call_args
    assert call_args.kwargs["calendarId"] == "test-calendar@example.com"

    event_body = call_args.kwargs["body"]
    assert event_body["summary"] == "Test Event"
    assert event_body["description"] == "Test Description"
    assert event_body["extendedProperties"]["private"]["source_id"] == (
        "test-source-123"
    )
    assert event_body["source"]["url"] == "https://example.com/tickets"


def test_upsert_event_updates_existing(calendar_client: CalendarClient) -> None:
    """Test upsert updates an existing event."""
    start_time = datetime(2025, 9, 10, 13, 0, 0, tzinfo=UTC)
    event_data = CalendarEventData(
        summary="Updated Event",
        description="Updated Description",
        start=start_time,
        end=start_time + timedelta(hours=1),
        source_id="test-source-123",
    )

    # Mock: existing event found
    mock_existing_event = {
        "id": "event123",
        "summary": "Old Event",
        "extendedProperties": {"private": {"source_id": "test-source-123"}},
    }
    calendar_client.service.events().list().execute.return_value = {
        "items": [mock_existing_event]
    }

    # Mock: update returns updated event
    mock_updated_event = {"id": "event123", "summary": "Updated Event"}
    calendar_client.service.events().update().execute.return_value = mock_updated_event

    created = calendar_client.upsert_event(event_data)

    assert created is False

    # Verify update was called
    call_args = calendar_client.service.events().update.call_args
    assert call_args.kwargs["calendarId"] == "test-calendar@example.com"
    assert call_args.kwargs["eventId"] == "event123"

    event_body = call_args.kwargs["body"]
    assert event_body["summary"] == "Updated Event"


def test_upsert_event_without_url(calendar_client: CalendarClient) -> None:
    """Test upserting an event without a URL."""
    start_time = datetime(2025, 9, 10, 13, 0, 0, tzinfo=UTC)
    event_data = CalendarEventData(
        summary="Test Event",
        description="Test Description",
        start=start_time,
        end=start_time + timedelta(hours=1),
        source_id="test-source-123",
    )

    # Mock: no existing event
    calendar_client.service.events().list().execute.return_value = {"items": []}

    mock_created_event = {"id": "new-event-123", "summary": "Test Event"}
    calendar_client.service.events().insert().execute.return_value = mock_created_event

    created = calendar_client.upsert_event(event_data)

    assert created is True

    # Verify no source field in event body
    call_args = calendar_client.service.events().insert.call_args
    event_body = call_args.kwargs["body"]
    assert "source" not in event_body
