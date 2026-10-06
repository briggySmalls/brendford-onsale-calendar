"""Tests for the web scraper."""

import json
import logging
from datetime import datetime
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from brentford_calendar.dates import LONDON
from brentford_calendar.scraper import extract_fixtures, scrape_fixtures

# Path to test fixtures
FIXTURE_HTML_PATH = Path(__file__).parent / "data" / "ticket-information.html"
EXPECTED_FIXTURES_PATH = Path(__file__).parent / "data" / "expected-fixtures.json"

BUY_NOW_CTA = (
    '<a data-testid="fixture-ticketing-card__sale-cta" '
    'href="https://tickets.example.com/buy">Buy Now</a>'
)
SOLD_OUT_CTA = (
    '<button data-testid="fixture-ticketing-card__sale-cta" disabled>Sold Out</button>'
)
DEFAULT_ROWS = [
    ("All members", "Tue 1 Sep, 14:00", "https://www.addevent.com/event/abc123")
]


def fixture_card(
    location: str = "Home",
    cta: str = BUY_NOW_CTA,
    rows: list[tuple[str, str, str | None]] | None = DEFAULT_ROWS,
) -> str:
    """Build the HTML of a fixture card, with a nullable on-sale rows list."""
    row_html = ""
    for label, on_sale, href in rows or []:
        link = f'<a href="{href}">Add to calendar</a>' if href else ""
        row_html += f"<li><p>{label}</p><p>{on_sale}</p>{link}</li>"
    rows_html = (
        f'<ul data-testid="fixture-ticketing-card__rows">{row_html}</ul>'
        if rows is not None
        else ""
    )
    return f"""
    <section data-testid="fixture-ticketing-card">
      <div>
        <div><img src="https://example.com/badge.png"/><h3>Test FC</h3>
          <p>{location}</p></div>
        <div><p>Sat 10 Oct '26</p><p>Premier League</p><p>15:00</p>
          <p>Category B</p></div>
        <div>{rows_html}
          <a data-testid="fixture-ticketing-card__find-out-more"
             href="/en/test-v-brentford-26-27">Find out more</a>
          {cta}
        </div>
      </div>
    </section>
    """


def test_extract_fixtures_from_real_html() -> None:
    """Test parsing fixtures from actual HTML fixture file.

    This test validates:
    - All fixtures are parsed correctly
    - Structure matches expected JSON fixture exactly
    - Pydantic validation passes
    """
    html_content = FIXTURE_HTML_PATH.read_text()
    fixtures = extract_fixtures(html_content)

    # Convert to dicts for comparison with expected JSON
    fixtures_dict = [f.model_dump(by_alias=True, mode="json") for f in fixtures]

    # Load expected fixtures
    expected_fixtures = json.loads(EXPECTED_FIXTURES_PATH.read_text())

    assert len(fixtures) == 6
    # All fixtures should match expected structure exactly
    assert fixtures_dict == expected_fixtures


def test_extract_fixtures_from_empty_html() -> None:
    """Test that empty HTML returns empty list."""
    fixtures = extract_fixtures("<html><body></body></html>")
    assert fixtures == []


def test_extract_fixture_card_fields() -> None:
    fixtures = extract_fixtures(f"<html><body>{fixture_card()}</body></html>")

    assert len(fixtures) == 1
    fixture = fixtures[0]
    assert fixture.title == "Test FC (H)"
    assert fixture.opposition_name == "Test FC"
    assert fixture.opposition_badge == "https://example.com/badge.png"
    assert fixture.is_home_fixture is True
    assert fixture.fixture_date == datetime(2026, 10, 10, 15, 0, tzinfo=LONDON)
    assert fixture.competition == "Premier League"
    assert fixture.category == "Category B"
    assert fixture.buy_now_url == "https://tickets.example.com/buy"
    assert fixture.find_out_more_url == (
        "https://www.brentfordfc.com/en/test-v-brentford-26-27"
    )
    assert [(w.label, w.on_sale_date, w.event_id) for w in fixture.windows] == [
        ("All members", datetime(2026, 9, 1, 14, 0, tzinfo=LONDON), "abc123")
    ]


def test_extract_fixture_card_away_fixture() -> None:
    fixture = extract_fixtures(fixture_card(location="Away"))[0]

    assert fixture.is_home_fixture is False
    assert fixture.title == "Test FC (A)"


def test_extract_fixture_card_sold_out_has_no_buy_now_url() -> None:
    fixture = extract_fixtures(fixture_card(cta=SOLD_OUT_CTA))[0]

    assert fixture.buy_now_url is None


def test_extract_fixture_card_without_rows_has_no_windows() -> None:
    fixture = extract_fixtures(fixture_card(rows=None))[0]

    assert fixture.windows == []


def test_extract_fixture_card_skips_row_without_calendar_link(
    caplog: pytest.LogCaptureFixture,
) -> None:
    rows = [
        ("All members", "Tue 1 Sep, 14:00", None),
        ("My Bees members", "Wed 2 Sep, 14:00", "https://www.addevent.com/event/xyz"),
    ]
    with caplog.at_level(logging.WARNING):
        fixture = extract_fixtures(fixture_card(rows=rows))[0]

    assert [w.event_id for w in fixture.windows] == ["xyz"]
    assert "Skipping unrecognised on-sale row" in caplog.text


def test_extract_fixture_card_rejects_unknown_location() -> None:
    with pytest.raises(ValueError, match="Unrecognised fixture card details"):
        extract_fixtures(fixture_card(location="Neutral"))


def test_scrape_fixtures_returns_fixtures(mocker: MockerFixture) -> None:
    mocker.patch(
        "brentford_calendar.scraper.fetch_page",
        return_value=f"<html><body>{fixture_card()}</body></html>",
    )

    assert len(scrape_fixtures()) == 1


def test_scrape_fixtures_fails_when_no_fixtures_found(mocker: MockerFixture) -> None:
    mocker.patch(
        "brentford_calendar.scraper.fetch_page",
        return_value="<html><body></body></html>",
    )

    with pytest.raises(ValueError, match="No fixtures found"):
        scrape_fixtures()
