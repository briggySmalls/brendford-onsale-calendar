"""Tests for ticket page date parsing."""

from datetime import UTC, datetime, timedelta

import pytest

from brentford_calendar.dates import (
    LONDON,
    parse_fixture_datetime,
    parse_window_datetime,
)


class TestParseFixtureDatetime:
    def test_british_summer_time(self) -> None:
        kickoff = parse_fixture_datetime("Sat 10 Oct '26", "15:00")
        assert kickoff == datetime(2026, 10, 10, 15, 0, tzinfo=LONDON)
        assert kickoff.utcoffset() == timedelta(hours=1)

    def test_greenwich_mean_time(self) -> None:
        kickoff = parse_fixture_datetime("Sat 31 Jan '26", "12:30")
        assert kickoff.astimezone(UTC) == datetime(2026, 1, 31, 12, 30, tzinfo=UTC)

    def test_weekday_mismatch(self) -> None:
        with pytest.raises(ValueError, match="Weekday"):
            parse_fixture_datetime("Sun 10 Oct '26", "15:00")

    @pytest.mark.parametrize(
        ("date_text", "time_text"),
        [("10 Oct 2026", "15:00"), ("Sat 10 Oct '26", "3pm"), ("", "")],
    )
    def test_malformed(self, date_text: str, time_text: str) -> None:
        with pytest.raises(ValueError, match="Unrecognised"):
            parse_fixture_datetime(date_text, time_text)


class TestParseWindowDatetime:
    fixture = datetime(2026, 10, 10, 15, 0, tzinfo=LONDON)

    def test_same_year_as_fixture(self) -> None:
        on_sale = parse_window_datetime("Tue 1 Sep, 14:00", self.fixture)
        assert on_sale == datetime(2026, 9, 1, 14, 0, tzinfo=LONDON)
        assert on_sale.astimezone(UTC).hour == 13

    def test_year_before_fixture_when_window_is_late_in_year(self) -> None:
        fixture = datetime(2027, 1, 2, 15, 0, tzinfo=LONDON)
        on_sale = parse_window_datetime("Mon 14 Dec, 14:00", fixture)
        assert on_sale == datetime(2026, 12, 14, 14, 0, tzinfo=LONDON)
        assert on_sale.utcoffset() == timedelta(0)

    def test_window_on_fixture_day(self) -> None:
        on_sale = parse_window_datetime("Sat 10 Oct, 09:00", self.fixture)
        assert on_sale == datetime(2026, 10, 10, 9, 0, tzinfo=LONDON)

    def test_weekday_mismatch(self) -> None:
        with pytest.raises(ValueError, match="Weekday"):
            parse_window_datetime("Wed 1 Sep, 14:00", self.fixture)

    def test_malformed(self) -> None:
        with pytest.raises(ValueError, match="Unrecognised"):
            parse_window_datetime("1 September at 2pm", self.fixture)
