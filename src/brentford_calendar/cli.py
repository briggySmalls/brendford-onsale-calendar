"""CLI for Brentford Calendar sync."""

import logging
import sys
from pathlib import Path

import click

from brentford_calendar.calendar_client import CalendarClient
from brentford_calendar.config import load_config_from_file
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
@click.option(
    "--credentials",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to Google service account JSON file",
)
@click.option(
    "--calendar-id",
    type=str,
    required=True,
    help="Google Calendar ID",
)
def main(
    verbose: int,
    membership: str,
    taps: int,
    credentials: Path,
    calendar_id: str,
) -> None:
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

        # Sync to Google Calendar
        logger.info("Syncing to Google Calendar")
        config = load_config_from_file(credentials, calendar_id)
        client = CalendarClient.from_config(config)

        # Sync each onsale fixture
        created, updated = 0, 0
        for onsale_fixture in onsale_fixtures:
            event_data = onsale_fixture.to_calendar_event_data()
            was_created = client.upsert_event(event_data)
            if was_created:
                created += 1
            else:
                updated += 1

        msg = f"Synced {len(onsale_fixtures)} events "
        msg += f"({created} created, {updated} updated)"
        click.echo(msg)

    except Exception as e:
        logger.error(f"Failed to process fixtures: {e}", exc_info=verbose >= 2)
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())
