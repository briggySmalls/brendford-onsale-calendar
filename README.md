# Brentford On-Sale Calendar

Sync Brentford FC ticket on-sale dates to Google Calendar automatically.

## Google Calendar Setup

### 1. Create a Google Cloud Project and Enable the Calendar API

Follow Google's quickstart guide to:
- Create a Google Cloud project
- Enable the Google Calendar API
- Create service account credentials

**Official Guide:** [Google Calendar API Quickstart](https://developers.google.com/calendar/api/quickstart/python)

### 2. Create Service Account Credentials

1. In the [Google Cloud Console](https://console.cloud.google.com/), navigate to **APIs & Services → Credentials**
2. Click **Create Credentials → Service Account**
3. Fill in the service account details and click **Create**
4. Click **Done** (no roles needed for accessing calendars you share with it)
5. Find your new service account in the list and click on it
6. Go to the **Keys** tab
7. Click **Add Key → Create new key → JSON**
8. Download the JSON key file and save it securely

**Official Guide:** [Creating service account credentials](https://cloud.google.com/iam/docs/service-accounts-create)

### 3. Share Your Calendar with the Service Account

1. Open [Google Calendar](https://calendar.google.com)
2. Find the calendar you want to use (or create a new one)
3. Click the three dots next to the calendar name → **Settings and sharing**
4. Scroll to **Share with specific people or groups**
5. Click **Add people and groups**
6. Enter the service account email (found in your JSON credentials file, e.g., `my-service@my-project.iam.gserviceaccount.com`)
7. Set permissions to **Make changes to events**
8. Click **Send**

### 4. Get Your Calendar ID

1. In the same calendar settings page, scroll to **Integrate calendar**
2. Copy the **Calendar ID** (e.g., `abc123@group.calendar.google.com`)

## Usage

```bash
brentford-calendar \
  --membership MY_BEES_MEMBERS \
  --taps 400 \
  --credentials /path/to/service-account.json \
  --calendar-id your-calendar-id@group.calendar.google.com
```

**Options:**
- `--membership`: Your membership type (`SEASON_TICKET`, `MY_BEES_MEMBERS`, or `MEMBERS`)
- `--taps`: Your TAPs count (default: 0)
- `--credentials`: Path to your Google service account JSON file
- `--calendar-id`: Your Google Calendar ID
- `-v` / `-vv`: Increase verbosity for debugging

## Automated Sync with GitHub Actions

You can set up automated daily syncing using GitHub Actions. The workflow runs daily at 6am UTC (6am GMT in winter / 7am BST in summer) and can also be triggered manually.

### Setup

1. **Create GitHub Secrets** (Settings → Secrets and variables → Actions → Secrets):
   - `GOOGLE_CREDENTIALS_JSON`: Paste the entire contents of your service account JSON file
   - `GOOGLE_CALENDAR_ID`: Your calendar ID (e.g., `abc123@group.calendar.google.com`)

2. **Create Repository Variables** (Settings → Secrets and variables → Actions → Variables tab):
   - `MEMBERSHIP_TYPE`: Your membership type (e.g., `MY_BEES_MEMBERS`)
   - `TAPS_COUNT`: Your TAPs count (e.g., `800`)

### Manual Trigger

To manually trigger a sync:
1. Go to the **Actions** tab in your GitHub repository
2. Select **Sync to Google Calendar** workflow
3. Click **Run workflow** → **Run workflow**

The workflow will show the sync output, including the number of events created or updated. If the sync fails, GitHub will send you an email notification.

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
