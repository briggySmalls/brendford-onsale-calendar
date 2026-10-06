"""Web scraper for Brentford FC ticket information."""

import logging
from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from brentford_calendar.dates import parse_fixture_datetime, parse_window_datetime
from brentford_calendar.models import FixtureData, SaleWindow

logger = logging.getLogger(__name__)

TICKETING_URL = "https://www.brentfordfc.com/en/ticket-information"

CARD_TEST_ID = "fixture-ticketing-card"
ROWS_TEST_ID = "fixture-ticketing-card__rows"
SALE_CTA_TEST_ID = "fixture-ticketing-card__sale-cta"
FIND_OUT_MORE_TEST_ID = "fixture-ticketing-card__find-out-more"


def fetch_page(url: str = TICKETING_URL, timeout: int = 30) -> str:
    """Fetch HTML content from the given URL.

    Args:
        url: The URL to fetch (defaults to Brentford ticketing page)
        timeout: Request timeout in seconds

    Returns:
        HTML content as string

    Raises:
        requests.RequestException: If the request fails
    """
    logger.info(f"Fetching page from {url}")
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    logger.debug(f"Received {len(response.text)} bytes")
    return response.text


def _parse_windows(card: Tag, fixture_date: datetime) -> list[SaleWindow]:
    """Parse the on-sale rows of a fixture card.

    Each row is a label and an on-sale date, with a link to an AddEvent
    reminder whose trailing path segment identifies the window.
    """
    rows = card.select_one(f'[data-testid="{ROWS_TEST_ID}"]')
    if rows is None:
        return []

    windows = []
    for row in rows.find_all("li"):
        texts = [p.get_text(strip=True) for p in row.find_all("p")]
        link = row.select_one("a[href]")
        if len(texts) != 2 or link is None:
            logger.warning(f"Skipping unrecognised on-sale row: {texts}")
            continue

        label, on_sale_text = texts
        windows.append(
            SaleWindow(
                label=label,
                on_sale_date=parse_window_datetime(on_sale_text, fixture_date),
                event_id=str(link["href"]).rstrip("/").rsplit("/", 1)[-1],
            )
        )
    return windows


def _parse_card(card: Tag) -> FixtureData:
    """Parse a single fixture-ticketing card."""
    opposition = card.select_one("h3")
    badge = card.select_one("img")
    find_out_more = card.select_one(f'[data-testid="{FIND_OUT_MORE_TEST_ID}"]')
    if opposition is None or badge is None or find_out_more is None:
        msg = "Fixture card is missing its opposition, badge or find out more link"
        raise ValueError(msg)

    # Class names are generated, so the fixture details are read by position:
    # home/away, date, competition, kick-off, category.
    details = [
        p.get_text(strip=True) for p in card.find_all("p") if not p.find_parent("ul")
    ]
    if len(details) != 5 or details[0] not in ("Home", "Away"):
        msg = f"Unrecognised fixture card details: {details}"
        raise ValueError(msg)
    location, date_text, competition, time_text, category = details

    is_home_fixture = location == "Home"
    fixture_date = parse_fixture_datetime(date_text, time_text)
    opposition_name = opposition.get_text(strip=True)

    sale_cta = card.select_one(f'a[data-testid="{SALE_CTA_TEST_ID}"][href]')

    return FixtureData(
        title=f"{opposition_name} ({'H' if is_home_fixture else 'A'})",
        opposition_name=opposition_name,
        opposition_badge=str(badge["src"]),
        is_home_fixture=is_home_fixture,
        fixture_date=fixture_date,
        competition=competition,
        category=category,
        buy_now_url=str(sale_cta["href"]) if sale_cta else None,
        find_out_more_url=urljoin(TICKETING_URL, str(find_out_more["href"])),
        windows=_parse_windows(card, fixture_date),
    )


def extract_fixtures(html_content: str) -> list[FixtureData]:
    """Extract fixture ticketing data from HTML.

    Parses HTML to find every fixture-ticketing card and reads the fixture
    details and on-sale windows from its text.

    Args:
        html_content: Raw HTML content

    Returns:
        List of FixtureData objects

    Raises:
        ValueError: If a card or one of its dates can't be understood
    """
    logger.info("Parsing HTML for fixture data")
    soup = BeautifulSoup(html_content, "html5lib")

    cards = soup.find_all("section", attrs={"data-testid": CARD_TEST_ID})
    logger.info(f"Found {len(cards)} fixture cards")

    fixtures = []
    for card in cards:
        fixture = _parse_card(card)
        fixtures.append(fixture)
        logger.debug(f"Parsed fixture: {fixture.title}")

    logger.info(f"Successfully parsed {len(fixtures)} fixtures")
    return fixtures


def scrape_fixtures() -> list[FixtureData]:
    """Scrape fixture ticketing data from Brentford FC website.

    Convenience function that fetches and parses the ticketing page.

    Returns:
        List of FixtureData objects

    Raises:
        requests.RequestException: If fetching fails
        ValueError: If no fixtures are found, or a fixture card can't be
            understood
    """
    html_content = fetch_page()
    fixtures = extract_fixtures(html_content)
    if not fixtures:
        msg = f"No fixtures found on {TICKETING_URL}; the page layout may have changed"
        raise ValueError(msg)
    return fixtures
