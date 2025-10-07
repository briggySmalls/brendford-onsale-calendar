"""Web scraper for Brentford FC ticket information."""

import html
import json
import logging
from typing import Any

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

TICKETING_URL = "https://www.brentfordfc.com/en/ticket-information"


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


def extract_fixtures(html_content: str) -> list[dict[str, Any]]:
    """Extract fixture ticketing data from HTML.

    Parses HTML to find all divs with data-component="FixtureTicketingModule",
    decodes the HTML entities in data-props, and parses the JSON data.

    Args:
        html_content: Raw HTML content

    Returns:
        List of fixture data dictionaries

    Raises:
        json.JSONDecodeError: If JSON parsing fails for any fixture
    """
    logger.info("Parsing HTML for fixture data")
    soup = BeautifulSoup(html_content, "html5lib")

    # Find all FixtureTicketingModule divs
    fixture_divs = soup.find_all("div", {"data-component": "FixtureTicketingModule"})
    logger.info(f"Found {len(fixture_divs)} fixture modules")

    fixtures = []
    for div in fixture_divs:
        raw_props = div.get("data-props", "")
        if not raw_props:
            logger.warning("Found div without data-props, skipping")
            continue

        # Decode HTML entities (&quot; -> ")
        decoded_props = html.unescape(raw_props)

        try:
            fixture_data = json.loads(decoded_props)
            fixtures.append(fixture_data)
            logger.debug(f"Parsed fixture: {fixture_data.get('title', 'Unknown')}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from data-props: {e}")
            logger.debug(f"Raw data: {decoded_props[:200]}...")
            raise

    logger.info(f"Successfully parsed {len(fixtures)} fixtures")
    return fixtures


def scrape_fixtures() -> list[dict[str, Any]]:
    """Scrape fixture ticketing data from Brentford FC website.

    Convenience function that fetches and parses the ticketing page.

    Returns:
        List of fixture data dictionaries

    Raises:
        requests.RequestException: If fetching fails
        json.JSONDecodeError: If parsing fails
    """
    html_content = fetch_page()
    return extract_fixtures(html_content)
