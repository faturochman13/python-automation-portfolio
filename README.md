# Python Automation Portfolio

Production-style Python samples showing how I build automation that clients can run
themselves — web scraping, REST API integration, and data-cleaning automation. Each
project is small but written with the reliability habits that matter on real work:
typed records, retry/backoff, timeouts, structured logging, a CLI, and a README.

> These are demo projects on public/synthetic data — no private data, no Terms violations.
> Full source + a short README is included for each, just like client deliverables.

## Projects

| Project | What it shows | Verified run |
|---|---|---|
| [**web_scraper/**](web_scraper/) | Scrape a website into clean CSV (pagination, retry/backoff, rate-limit) | 60 books → CSV |
| [**api_integration/**](api_integration/) | REST API client → CSV (live ECB FX rates, retry, validation, conversion) | `100 USD = 87.71 EUR / 75.65 GBP` |
| [**data_automation/**](data_automation/) | Clean a messy CSV (validate emails, dedupe, normalize) + report | 10 rows → 5 clean (2 dupes, 2 bad emails, 1 no-name dropped) |

## What I build for clients

- **Web scraping** → structured data (CSV / Excel / Google Sheets)
- **API integration & glue** (Gmail, Sheets, Slack, Notion, REST, webhooks)
- **Automation bots** (login, form-fill, scheduled jobs) with error handling + logging
- **LLM / AI integration** — wiring language models into your workflow for smart parsing & decisions

## Run any project

```bash
cd <project_folder>
pip install -r requirements.txt   # where present (data_automation is stdlib-only)
python <script>.py --help
```

## Tech

Python 3 · `requests` · `BeautifulSoup` · standard library. Cross-platform (Windows / macOS / Linux).

---

Built by **Faturochman Maulana** — Python Automation & Web Scraping.
Available for work on [Upwork](https://www.upwork.com/) and [Fiverr](https://www.fiverr.com/faturochman13).
