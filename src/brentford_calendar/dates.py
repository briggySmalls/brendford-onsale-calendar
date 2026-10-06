"""Parsing of the abbreviated dates shown on the Brentford FC ticket page."""

import re
from datetime import datetime
from zoneinfo import ZoneInfo

LONDON = ZoneInfo("Europe/London")

_FIXTURE_DATE_RE = re.compile(r"^(\w{3}) (\d{1,2}) (\w{3}) '(\d{2})$")
_TIME_RE = re.compile(r"^(\d{1,2}):(\d{2})$")
_WINDOW_DATE_RE = re.compile(r"^(\w{3}) (\d{1,2}) (\w{3}), (\d{1,2}):(\d{2})$")


def _month_number(abbreviation: str) -> int:
    return datetime.strptime(abbreviation, "%b").month


def _check_weekday(parsed: datetime, weekday: str, text: str) -> None:
    if parsed.strftime("%a").lower() != weekday.lower():
        msg = f"Weekday does not match date in {text!r}"
        raise ValueError(msg)


def parse_fixture_datetime(date_text: str, time_text: str) -> datetime:
    """Parse a fixture's kick-off from its date and time labels.

    Args:
        date_text: Date label like "Sat 10 Oct '26"
        time_text: Kick-off label like "15:00"

    Returns:
        Kick-off as a timezone-aware datetime in Europe/London

    Raises:
        ValueError: If either label is malformed or the weekday does not
            match the date
    """
    date_match = _FIXTURE_DATE_RE.match(date_text.strip())
    time_match = _TIME_RE.match(time_text.strip())
    if date_match is None:
        msg = f"Unrecognised fixture date {date_text!r}"
        raise ValueError(msg)
    if time_match is None:
        msg = f"Unrecognised kick-off time {time_text!r}"
        raise ValueError(msg)

    weekday, day, month, year = date_match.groups()
    kickoff = datetime(
        2000 + int(year),
        _month_number(month),
        int(day),
        int(time_match.group(1)),
        int(time_match.group(2)),
        tzinfo=LONDON,
    )
    _check_weekday(kickoff, weekday, date_text)
    return kickoff


def parse_window_datetime(text: str, fixture_datetime: datetime) -> datetime:
    """Parse an on-sale window label, which omits the year.

    A window always opens before its fixture, so the year is the latest one
    that places the window on or before the fixture's kick-off.

    Args:
        text: On-sale label like "Tue 1 Sep, 14:00"
        fixture_datetime: Kick-off of the fixture the window belongs to

    Returns:
        On-sale time as a timezone-aware datetime in Europe/London

    Raises:
        ValueError: If the label is malformed or the weekday does not match
            the inferred date
    """
    match = _WINDOW_DATE_RE.match(text.strip())
    if match is None:
        msg = f"Unrecognised on-sale date {text!r}"
        raise ValueError(msg)

    weekday, day, month, hour, minute = match.groups()
    parts = (_month_number(month), int(day), int(hour), int(minute))

    on_sale = datetime(fixture_datetime.year, *parts, tzinfo=LONDON)
    if on_sale > fixture_datetime:
        on_sale = datetime(fixture_datetime.year - 1, *parts, tzinfo=LONDON)
    _check_weekday(on_sale, weekday, text)
    return on_sale
