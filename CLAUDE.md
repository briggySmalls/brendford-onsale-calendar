# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Brentford On-Sale Calendar syncs Brentford FC ticket on-sale dates to Google Calendar. The tool scrapes the Brentford FC website, parses ticket sale windows, filters by membership tier and TAPs, and optionally syncs to Google Calendar.

## Project Structure

- `src/brentford_calendar/` - Main package
  - `cli.py` - Click CLI entry point
  - `scraper.py` - Web scraping logic
  - `models.py` - Pydantic data models
  - `calendar_client.py` - Google Calendar API integration
  - `config.py` - Configuration management
- `tests/` - Test suite
- `pyproject.toml` - Project configuration and dependencies
- `.python-version` - Python 3.13.0
- `Makefile` - Development commands
- `IMPLEMENTATION_PLAN.md` - Detailed implementation plan with commit structure

## Development Commands

**IMPORTANT:** Always use the Makefile for development commands. See README.md for detailed setup instructions.

```bash
# Run all checks (linting, formatting, type checking)
make check

# Auto-fix linting issues
make fix

# Run tests
make test
```

For full development setup instructions, refer to README.md.

## Technology Stack

- **Python 3.13+** with uv package manager
- **Web scraping**: beautifulsoup4, requests, html5lib
- **Data validation**: pydantic
- **Google Calendar**: google-auth, google-api-python-client
- **CLI**: click
- **Testing**: pytest, pytest-mock
- **Code quality**: ruff (formatting + linting), mypy (type checking), pre-commit

## Key Architecture

- `FixtureData` → `ProcessedFixtureData` → `OnsaleFixtureData` → `CalendarEventData`
- Membership hierarchy: SEASON_TICKET > MY_BEES_MEMBERS > MEMBERS
- Idempotency via `source_id` in Google Calendar extended properties
