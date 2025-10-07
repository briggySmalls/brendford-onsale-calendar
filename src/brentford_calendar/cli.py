"""CLI for Brentford Calendar sync."""

import logging
import sys

import click


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

    logger.info("Sync started")
    click.echo("Brentford Calendar Sync - Coming soon!")
    logger.info("Sync completed")


if __name__ == "__main__":
    sys.exit(main())
