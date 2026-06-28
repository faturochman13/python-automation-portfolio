#!/usr/bin/env python3
"""
fx_rates_client.py — Production-style REST API integration (portfolio sample).

Pulls foreign-exchange rates from the Frankfurter API (free, no API key,
backed by European Central Bank data) and writes a clean CSV. Demonstrates
the qualities clients pay for in an API-integration gig: a typed client,
request params, retry with backoff, timeout, structured logging, optional
amount conversion, and a run summary.

Usage:
    python fx_rates_client.py --base USD --symbols EUR,GBP,JPY,IDR --out rates.csv
    python fx_rates_client.py --base EUR --symbols USD --amount 250
"""
from __future__ import annotations

import argparse
import csv
import logging
import sys
import time
from dataclasses import dataclass, asdict, fields

import requests

API_URL = "https://api.frankfurter.dev/v1/latest"

log = logging.getLogger("fx_rates_client")


@dataclass
class Rate:
    base: str
    symbol: str
    rate: float
    date: str


def make_session(retries: int = 3, backoff: float = 0.6) -> requests.Session:
    """Session with automatic retry + exponential backoff on transient errors."""
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry

    retry = Retry(
        total=retries,
        backoff_factor=backoff,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    session = requests.Session()
    session.headers.update({"User-Agent": "portfolio-fx-client/1.0 (+demo)"})
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def fetch_rates(base: str, symbols: list[str], session: requests.Session) -> list[Rate]:
    """Call the API once and map the JSON response into typed Rate rows."""
    params = {"base": base, "symbols": ",".join(symbols)}
    resp = session.get(API_URL, params=params, timeout=15)
    resp.raise_for_status()
    payload = resp.json()

    if "rates" not in payload:
        raise ValueError(f"unexpected API response: {payload!r}")

    date = payload.get("date", "")
    rows = [
        Rate(base=base, symbol=sym, rate=float(val), date=date)
        for sym, val in payload["rates"].items()
    ]
    rows.sort(key=lambda r: r.symbol)
    return rows


def write_csv(rows: list[Rate], path: str) -> None:
    cols = [f.name for f in fields(Rate)]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=cols)
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def summarize(rows: list[Rate], amount: float | None) -> str:
    if not rows:
        return "No rates returned."
    parts = [f"{len(rows)} rates as of {rows[0].date} (base {rows[0].base})"]
    if amount is not None:
        conv = ", ".join(f"{amount:g} {rows[0].base}={amount * r.rate:.2f} {r.symbol}" for r in rows)
        parts.append(conv)
    return " | ".join(parts)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch FX rates from the Frankfurter API to CSV.")
    parser.add_argument("--base", default="USD", help="base currency (e.g. USD)")
    parser.add_argument("--symbols", default="EUR,GBP,JPY,IDR", help="comma-separated target currencies")
    parser.add_argument("--amount", type=float, default=None, help="optional amount to convert in summary")
    parser.add_argument("--out", default="rates.csv", help="output CSV path")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(message)s",
        datefmt="%H:%M:%S",
    )

    symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
    session = make_session()
    start = time.perf_counter()
    try:
        rows = fetch_rates(args.base.upper(), symbols, session)
    except (requests.RequestException, ValueError) as exc:
        log.error("failed to fetch rates: %s", exc)
        return 1
    write_csv(rows, args.out)
    elapsed = time.perf_counter() - start

    log.info("wrote %d rows -> %s (%.2fs)", len(rows), args.out, elapsed)
    print(summarize(rows, args.amount))
    return 0 if rows else 1


if __name__ == "__main__":
    sys.exit(main())
