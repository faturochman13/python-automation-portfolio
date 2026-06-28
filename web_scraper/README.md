# Book Scraper — Python Automation Sample

A small, **production-style** web scraper that turns a website into clean CSV data.
Built as a portfolio sample to show how I write automation: not a throwaway script,
but code with the reliability habits that matter in real projects.

> Target: [`books.toscrape.com`](https://books.toscrape.com) — a public sandbox built
> specifically for scraping practice. No private data, no Terms violations.

## What it demonstrates

| Quality clients ask for | How this script does it |
|---|---|
| **Reliability** | Automatic retry + exponential backoff on `429/5xx` errors |
| **Politeness** | Configurable rate-limit (`--delay`) between requests |
| **Observability** | Structured logging with timestamps (`-v` for debug) |
| **Clean output** | Typed records → CSV (`title, price, rating, in_stock, url`) |
| **Configurable** | CLI flags for pages, output path, delay — no code edits needed |
| **Cross-platform** | ASCII-safe output; runs on Windows / macOS / Linux |

## Usage

```bash
pip install -r requirements.txt
python book_scraper.py --pages 3 --out books.csv --delay 0.5
```

## Example run

```
04:07:07 INFO    page 1/3 -> 20 books
04:07:08 INFO    page 2/3 -> 20 books
04:07:08 INFO    page 3/3 -> 20 books
04:07:09 INFO    wrote 60 rows -> books.csv (2.7s)
Scraped 60 books | avg price GBP 35.00 | 60/60 in stock | top-rated: 'Sapiens: A Brief History of Humankind' (5 stars)
```

Sample output (`books.csv`):

| title | price_gbp | rating | in_stock | product_url |
|---|---|---|---|---|
| A Light in the Attic | 51.77 | 3 | True | …/a-light-in-the-attic_1000/ |
| Tipping the Velvet | 53.74 | 1 | True | …/tipping-the-velvet_999/ |

## What I can build for you

This same foundation extends to: **API integrations** (Gmail, Sheets, Slack, REST),
**login-based automation bots**, **scheduled jobs**, and **AI-assisted parsing**
(OpenAI / Claude). Message me with your task and I'll scope it precisely.
