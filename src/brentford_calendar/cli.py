"""CLI for Brentford Calendar sync."""

import json
import logging
import sys

import click

from brentford_calendar.models import (
    MembershipType,
    OnsaleFixtureData,
    ProcessedFixtureData,
)
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
@click.option(
    "--membership",
    type=click.Choice(
        [m.name for m in MembershipType],
        case_sensitive=False,
    ),
    required=True,
    help="Membership type (e.g., MY_BEES_MEMBERS)",
)
@click.option(
    "--taps",
    type=int,
    default=0,
    help="Number of TAPs you have (default: 0)",
)
def main(verbose: int, membership: str, taps: int) -> None:
    """Sync Brentford FC ticket on-sale dates to Google Calendar."""
    setup_logging(verbose)
    logger = logging.getLogger(__name__)

    try:
        logger.info("Fetching fixtures from Brentford FC website")
        raw_fixtures = scrape_fixtures()
        logger.info(f"Found {len(raw_fixtures)} raw fixtures")

        # Convert membership string to enum
        membership_type = MembershipType[membership.upper()]
        logger.info(f"Filtering for {membership_type.value} with {taps} TAPs")

        # Process fixtures: FixtureData -> ProcessedFixtureData -> OnsaleFixtureData
        onsale_fixtures = []
        for fixture in raw_fixtures:
            processed = ProcessedFixtureData.from_fixture_data(fixture)
            onsale = OnsaleFixtureData.from_processed_fixture_data(
                processed, membership_type, taps
            )
            if onsale is not None:
                onsale_fixtures.append(onsale)

        logger.info(
            f"Found {len(onsale_fixtures)} fixtures with eligible on-sale dates"
        )

        # Convert Pydantic models to dicts and output as formatted JSON
        fixtures_dict = [f.model_dump(by_alias=True) for f in onsale_fixtures]
        click.echo(json.dumps(fixtures_dict, indent=2, default=str))

    except Exception as e:
        logger.error(f"Failed to process fixtures: {e}", exc_info=verbose >= 2)
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())
