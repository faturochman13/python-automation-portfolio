# FX Rates API Client — Python API Integration Sample

A small, **production-style** REST API client that pulls live foreign-exchange
rates and turns them into clean CSV. Built as a portfolio sample to show how I
integrate third-party APIs: typed responses, retries, and clean output — not a
throwaway `requests.get()`.

> Source: [Frankfurter API](https://frankfurter.dev) — free, no API key, rates
> published by the European Central Bank. No credentials, no Terms violations.

## What it demonstrates

| Quality clients ask for | How this script does it |
|---|---|
| **Reliability** | Automatic retry + exponential backoff on `429/5xx` errors |
| **Correct API use** | Query params (`base`, `symbols`), timeout, status check |
| **Validation** | Guards against unexpected JSON shapes before parsing |
| **Observability** | Structured logging with timestamps (`-v` for debug) |
| **Clean output** | Typed records → CSV (`base, symbol, rate, date`) |
| **Useful extras** | Optional `--amount` to convert and report in one call |

## Usage

```bash
pip install -r requirements.txt
python fx_rates_client.py --base USD --symbols EUR,GBP,JPY,IDR --amount 100 --out rates.csv
```

## Example run

```
01:52:02 INFO    wrote 4 rows -> rates.csv (0.69s)
4 rates as of 2026-06-26 (base USD) | 100 USD=87.71 EUR, 100 USD=75.65 GBP, 100 USD=1785900.00 IDR, 100 USD=16165.00 JPY
```

Sample output (`rates.csv`):

| base | symbol | rate | date |
|---|---|---|---|
| USD | EUR | 0.87712 | 2026-06-26 |
| USD | GBP | 0.75654 | 2026-06-26 |
| USD | JPY | 161.65 | 2026-06-26 |

## What I can build for you

This same foundation extends to **any REST/GraphQL API**: payment & FX data,
CRM sync (HubSpot/Salesforce), Google Sheets/Slack/Notion automations, webhook
handlers, and scheduled data pulls. Send me the API docs and I'll scope it.
