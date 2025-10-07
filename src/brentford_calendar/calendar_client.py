"""Google Calendar API client for managing ticket sale events."""

import logging
from datetime import timedelta
from typing import Any

from google.oauth2 import service_account
from googleapiclient.discovery import build

from brentford_calendar.config import GoogleCalendarConfig
from brentford_calendar.models import CalendarEventData

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/calendar"]


class CalendarClient:
    """Client for interacting with Google Calendar API."""

    def __init__(self, calendar_id: str, service: Any):
        """Initialize the calendar client.

        Args:
            calendar_id: Target Google Calendar ID
            service: Google Calendar API service instance
        """
        self.calendar_id = calendar_id
        self.service = service
        logger.info(f"Initialized CalendarClient for calendar {calendar_id}")

    @staticmethod
    def from_config(config: GoogleCalendarConfig) -> "CalendarClient":
        """Create CalendarClient from configuration.

        This factory method handles credential creation and service building.

        Args:
            config: Google Calendar configuration

        Returns:
            CalendarClient instance
        """
        credentials = service_account.Credentials.from_service_account_info(
            config.service_account_info, scopes=SCOPES
        )
        service = build("calendar", "v3", credentials=credentials)
        return CalendarClient(calendar_id=config.calendar_id, service=service)

    def _get_event_by_source_id(self, source_id: str) -> dict[str, Any] | None:
        """Find an event by source_id in extendedProperties.

        Args:
            source_id: Unique identifier for the event source

        Returns:
            Event dict if found, None otherwise
        """
        logger.debug(f"Searching for event with source_id={source_id}")

        events_result = (
            self.service.events()
            .list(
                calendarId=self.calendar_id,
                privateExtendedProperty=f"source_id={source_id}",
                maxResults=1,
            )
            .execute()
        )

        events = events_result.get("items", [])
        if events:
            logger.debug(f"Found existing event: {events[0]['id']}")
            return dict(events[0])

        logger.debug("No existing event found")
        return None

    def _create_event(self, event_data: CalendarEventData) -> None:
        """Create a new calendar event.

        Args:
            event_data: Event data to create
        """
        logger.info(f"Creating event: {event_data.summary}")

        start_dt = event_data.start
        end_dt = event_data.end or (start_dt + timedelta(hours=1))

        event_body = {
            "summary": event_data.summary,
            "description": event_data.description,
            "start": {"dateTime": start_dt.isoformat(), "timeZone": "UTC"},
            "end": {"dateTime": end_dt.isoformat(), "timeZone": "UTC"},
            "extendedProperties": {"private": {"source_id": event_data.source_id}},
        }

        if event_data.url:
            event_body["source"] = {"url": event_data.url, "title": "Ticket Info"}

        result = (
            self.service.events()
            .insert(
                calendarId=self.calendar_id,
                body=event_body,  # type: ignore[arg-type]  # Stubs expect strict TypedDict, API accepts partial dicts
            )
            .execute()
        )

        logger.info(f"Created event {result['id']}")

    def _update_event(self, event_id: str, event_data: CalendarEventData) -> None:
        """Update an existing calendar event.

        Args:
            event_id: Google Calendar event ID
            event_data: New event data
        """
        logger.info(f"Updating event {event_id}: {event_data.summary}")

        start_dt = event_data.start
        end_dt = event_data.end or (start_dt + timedelta(hours=1))

        event_body = {
            "summary": event_data.summary,
            "description": event_data.description,
            "start": {"dateTime": start_dt.isoformat(), "timeZone": "UTC"},
            "end": {"dateTime": end_dt.isoformat(), "timeZone": "UTC"},
            "extendedProperties": {"private": {"source_id": event_data.source_id}},
        }

        if event_data.url:
            event_body["source"] = {"url": event_data.url, "title": "Ticket Info"}

        self.service.events().update(
            calendarId=self.calendar_id,
            eventId=event_id,
            body=event_body,  # type: ignore[arg-type]  # Stubs expect strict TypedDict, API accepts partial dicts
        ).execute()

        logger.info(f"Updated event {event_id}")

    def upsert_event(self, event_data: CalendarEventData) -> bool:
        """Create or update an event based on source_id.

        Args:
            event_data: Event data to upsert

        Returns:
            True if event was created, False if updated
        """
        existing_event = self._get_event_by_source_id(event_data.source_id)

        if existing_event:
            self._update_event(existing_event["id"], event_data)
            return False
        else:
            self._create_event(event_data)
            return True
