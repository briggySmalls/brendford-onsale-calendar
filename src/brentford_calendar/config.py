"""Configuration management for Google Calendar integration."""

import json
import logging
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class GoogleCalendarConfig(BaseModel):
    """Configuration for Google Calendar integration."""

    service_account_info: dict[str, Any] = Field(
        description="Google service account credentials"
    )
    calendar_id: str = Field(description="Google Calendar ID")


def load_config_from_file(
    credentials_path: Path, calendar_id: str
) -> GoogleCalendarConfig:
    """Load Google Calendar configuration from service account file.

    Args:
        credentials_path: Path to Google service account JSON file
        calendar_id: Google Calendar ID

    Returns:
        GoogleCalendarConfig instance

    Raises:
        FileNotFoundError: If credentials file doesn't exist
        json.JSONDecodeError: If credentials file is invalid JSON
    """
    logger.info(f"Loading credentials from {credentials_path}")

    if not credentials_path.exists():
        raise FileNotFoundError(f"Credentials file not found: {credentials_path}")

    with credentials_path.open() as f:
        service_account_data: dict[str, Any] = json.load(f)

    return GoogleCalendarConfig(
        service_account_info=service_account_data,
        calendar_id=calendar_id,
    )
