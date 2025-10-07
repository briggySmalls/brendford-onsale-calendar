"""Tests for configuration module."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from brentford_calendar.config import GoogleCalendarConfig, load_config_from_file


def test_google_calendar_config_from_dict() -> None:
    """Test creating config from dict."""
    service_account_data = {
        "type": "service_account",
        "project_id": "test-project",
        "private_key_id": "key123",
        "private_key": "-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----",
        "client_email": "test@test.iam.gserviceaccount.com",
    }

    config = GoogleCalendarConfig(
        service_account_info=service_account_data,
        calendar_id="test-calendar@example.com",
    )

    assert config.service_account_info == service_account_data
    assert config.calendar_id == "test-calendar@example.com"


def test_load_config_from_file(tmp_path: Path) -> None:
    """Test loading config from file."""
    service_account_data = {
        "type": "service_account",
        "project_id": "test-project",
        "private_key_id": "key123",
        "private_key": "-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----",
        "client_email": "test@test.iam.gserviceaccount.com",
        "client_id": "123456",
    }

    # Create temporary credentials file
    creds_file = tmp_path / "credentials.json"
    creds_file.write_text(json.dumps(service_account_data))

    config = load_config_from_file(creds_file, "test-calendar@example.com")

    assert config.service_account_info == service_account_data
    assert config.calendar_id == "test-calendar@example.com"


def test_load_config_file_not_found() -> None:
    """Test error when credentials file doesn't exist."""
    non_existent_path = Path("/nonexistent/path.json")

    with pytest.raises(FileNotFoundError, match="Credentials file not found"):
        load_config_from_file(non_existent_path, "test-calendar@example.com")


def test_load_config_invalid_json(tmp_path: Path) -> None:
    """Test error when credentials file has invalid JSON."""
    bad_json_file = tmp_path / "bad.json"
    bad_json_file.write_text("not valid json")

    with pytest.raises(json.JSONDecodeError):
        load_config_from_file(bad_json_file, "test-calendar@example.com")


def test_config_validation_error() -> None:
    """Test that invalid config raises ValidationError."""
    with pytest.raises(ValidationError):
        GoogleCalendarConfig(
            service_account_info="not a dict",  # type: ignore[arg-type]
            calendar_id="test-calendar@example.com",
        )
