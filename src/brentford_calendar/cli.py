"""CLI for Brentford Calendar sync."""

import json
import logging
import sys

import click

from brentford_calendar.scraper import scrape_fixtures


def setup_logging(verbose: int) -> None:
    """Configure logging based on verbosity level."""
    level = logging.WARNING
    if verbose == 1:
        level = logging.INFO
    elif verbose >= 2:
        level = logging.DEBUG

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


@click.command()
@click.option(
    "--verbose",
    "-v",
    count=True,
    help="Increase verbosity (can be repeated: -v, -vv)",
)
def main(verbose: int) -> None:
    """Sync Brentford FC ticket on-sale dates to Google Calendar."""
    setup_logging(verbose)
    logger = logging.getLogger(__name__)

    try:
        logger.info("Fetching fixtures from Brentford FC website")
        fixtures = scrape_fixtures()
        logger.info(f"Found {len(fixtures)} fixtures")

        # Output as formatted JSON
        click.echo(json.dumps(fixtures, indent=2))

    except Exception as e:
        logger.error(f"Failed to scrape fixtures: {e}", exc_info=verbose >= 2)
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())
