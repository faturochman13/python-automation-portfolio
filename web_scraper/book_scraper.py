#!/usr/bin/env python3
"""
book_scraper.py — Production-style web scraper (portfolio sample).

Scrapes a public practice site (books.toscrape.com — built for scraping demos)
into clean CSV. Demonstrates the qualities clients pay for: configurable CLI,
retry with backoff, rate-limiting, structured logging, and a run summary.

Usage:
    python book_scraper.py --pages 3 --out books.csv --delay 0.5
"""
from __future__ import annotations

import argparse
import csv
import logging
import re
import sys
import time
from dataclasses import dataclass, asdict, fields
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"
RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

log = logging.getLogger("book_scraper")


@dataclass
class Book:
    title: str
    price_gbp: float
    rating: int
    in_stock: bool
    product_url: str


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
    session.headers.update({"User-Agent": "portfolio-scraper/1.0 (+demo)"})
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def parse_page(html: str, page_url: str) -> list[Book]:
    soup = BeautifulSoup(html, "html.parser")
    books: list[Book] = []
    for card in soup.select("article.product_pod"):
        title = card.h3.a["title"].strip()
        price_raw = card.select_one("p.price_color").get_text(strip=True)
        price_match = re.search(r"[\d.]+", price_raw.replace(",", ""))
        price = float(price_match.group()) if price_match else 0.0
        rating_cls = card.select_one("p.star-rating")["class"][1]
        rating = RATING_MAP.get(rating_cls, 0)
        in_stock = "In stock" in card.select_one("p.instock.availability").get_text()
        href = card.h3.a["href"]
        books.append(
            Book(
                title=title,
                price_gbp=price,
                rating=rating,
                in_stock=in_stock,
                product_url=urljoin(page_url, href),
            )
        )
    return books


def scrape(pages: int, delay: float, session: requests.Session) -> list[Book]:
    all_books: list[Book] = []
    for page in range(1, pages + 1):
        url = BASE_URL.format(page)
        try:
            resp = session.get(url, timeout=15)
            resp.raise_for_status()
        except requests.RequestException as exc:
            log.warning("page %d failed (%s) — skipping", page, exc)
            continue
        page_books = parse_page(resp.text, url)
        log.info("page %d/%d -> %d books", page, pages, len(page_books))
        all_books.extend(page_books)
        time.sleep(delay)  # be polite: rate-limit between requests
    return all_books


def write_csv(books: list[Book], path: str) -> None:
    cols = [f.name for f in fields(Book)]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=cols)
        writer.writeheader()
        for book in books:
            writer.writerow(asdict(book))


def summarize(books: list[Book]) -> str:
    if not books:
        return "No books scraped."
    avg = sum(b.price_gbp for b in books) / len(books)
    in_stock = sum(b.in_stock for b in books)
    top = max(books, key=lambda b: b.rating)
    return (
        f"Scraped {len(books)} books | avg price GBP {avg:.2f} | "
        f"{in_stock}/{len(books)} in stock | "
        f"top-rated: {top.title!r} ({top.rating} stars)"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scrape books.toscrape.com to CSV.")
    parser.add_argument("--pages", type=int, default=3, help="number of pages")
    parser.add_argument("--out", default="books.csv", help="output CSV path")
    parser.add_argument("--delay", type=float, default=0.5, help="seconds between requests")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(message)s",
        datefmt="%H:%M:%S",
    )

    session = make_session()
    start = time.perf_counter()
    books = scrape(args.pages, args.delay, session)
    write_csv(books, args.out)
    elapsed = time.perf_counter() - start

    log.info("wrote %d rows -> %s (%.1fs)", len(books), args.out, elapsed)
    print(summarize(books))
    return 0 if books else 1


if __name__ == "__main__":
    sys.exit(main())
