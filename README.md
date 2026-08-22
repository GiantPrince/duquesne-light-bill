# duquesne-light-bill

Generate a daily bill report for your Duquesne Light account.

## Features
**Daily Cost + Hourly Cost Graph** — Get a daily cost summary with an hourly usage graph.
**Email Report** — Automatically receive the report by email.
**Scheduled Reports** — Use GitHub Actions to generate the report daily.

## Configuration

- `DUQUESNE_USERNAME` — Your Duquesne Light username
- `DUQUESNE_PASSWORD` — Your Duquesne Light password
- `GMAIL_ADDRESS` — Gmail address used to send the report
- `GMAIL_APP_PASSWORD` — Gmail App Password used for SMTP

Go to **GitHub → Settings → Secrets and variables → Actions** and add these as **Repository secrets**.

## How

Uses headless Playwright to log in to your Duquesne Light account, extract daily usage and cost data, capture the usage graph, and email the report to you.