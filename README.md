# Brentford On-Sale Calendar

Sync Brentford FC ticket on-sale dates to Google Calendar automatically.

## Development Setup

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager

### Getting Started

```bash
# Install dependencies
uv sync --all-extras

# Install pre-commit hooks
uv run pre-commit install

# Run all checks (linting, formatting, type checking)
make check

# Auto-fix linting issues
make fix

# Run tests
make test
```

## Project Structure

```
src/brentford_calendar/  # Main package
tests/                   # Test suite
.github/workflows/       # CI/CD workflows
```
