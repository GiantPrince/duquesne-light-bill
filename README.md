# duquesne-light-bill

Generate a bill report for your Duquesne Light account.

## Features
**Daily Cost + Hourly Cost Graph** — Get a daily cost summary with an hourly usage graph.

**Email Report** — Automatically receive the report by email.

**Scheduled Reports** — Use GitHub Actions to generate the report as scheduled.

## Configuration

The application is configured using environment variables.

### Required configuration

| Variable | Description |
|---|---|
| `LAST_N_DAYS` | Number of days of Duquesne Light data to include in the report |
| `EMAIL_SUBJECT` | Subject of the report email |
| `DUQUESNE_LIGHT_USERNAME` | Your Duquesne Light account username |
| `DUQUESNE_LIGHT_PASSWORD` | Your Duquesne Light account password |
| `GMAIL_SENDER` | Gmail address used to send the report |
| `GMAIL_APP_PASSWORD` | Gmail App Password used for SMTP authentication |
| `EMAIL_RECEIVER` | Email address(es) that will receive the report. Multiple addresses can be separated by commas. |

### Example

```env
LAST_N_DAYS=7
EMAIL_SUBJECT=Weekly Duquesne Bill Chart

DUQUESNE_LIGHT_USERNAME=your_duquesne_username
DUQUESNE_LIGHT_PASSWORD=your_duquesne_password

GMAIL_SENDER=your@gmail.com
GMAIL_APP_PASSWORD=your_gmail_app_password
EMAIL_RECEIVER=person1@example.com,person2@example.com
```

## How It Works

Uses headless Playwright to log in to your Duquesne Light account, extract daily usage and cost data, capture the usage graph, and email the report to you.