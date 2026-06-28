#!/usr/bin/env python3
"""
data_cleaner.py — Production-style data-cleaning automation (portfolio sample).

Takes a messy contact list (the kind exported from a CRM or sign-up form) and
produces a clean, validated, de-duplicated CSV plus a quality report. This is
the "automate the boring spreadsheet work" task clients pay for: trims junk,
normalizes casing, validates emails/phones, drops duplicates and invalid rows,
and tells you exactly what it changed.

Usage:
    python data_cleaner.py --in contacts_messy.csv --out contacts_clean.csv
    python data_cleaner.py --in contacts_messy.csv --out clean.csv --report report.txt
"""
from __future__ import annotations

import argparse
import csv
import logging
import re
import sys
from dataclasses import dataclass

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[a-z]{2,}$", re.IGNORECASE)

log = logging.getLogger("data_cleaner")


@dataclass
class Stats:
    read: int = 0
    written: int = 0
    duplicates: int = 0
    invalid_email: int = 0
    missing_name: int = 0
    phones_normalized: int = 0


def normalize_name(raw: str) -> str:
    """Collapse whitespace and title-case a person/company name."""
    return re.sub(r"\s+", " ", raw).strip().title()


def normalize_email(raw: str) -> str:
    return raw.strip().lower()


def normalize_phone(raw: str) -> tuple[str, bool]:
    """Return (E.164-ish digits, changed?). Keeps a leading +, strips the rest."""
    cleaned = raw.strip()
    plus = cleaned.startswith("+")
    digits = re.sub(r"\D", "", cleaned)
    result = ("+" + digits) if plus else digits
    return result, (result != raw.strip())


def clean_rows(rows: list[dict], stats: Stats) -> list[dict]:
    seen_emails: set[str] = set()
    out: list[dict] = []
    for row in rows:
        stats.read += 1
        name = normalize_name(row.get("name", "") or "")
        email = normalize_email(row.get("email", "") or "")
        phone_raw = row.get("phone", "") or ""

        if not name:
            stats.missing_name += 1
            continue
        if not EMAIL_RE.match(email):
            stats.invalid_email += 1
            continue
        if email in seen_emails:
            stats.duplicates += 1
            continue

        seen_emails.add(email)
        phone, changed = normalize_phone(phone_raw)
        if changed:
            stats.phones_normalized += 1
        out.append({"name": name, "email": email, "phone": phone})

    stats.written = len(out)
    return out


def read_csv(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def write_csv(rows: list[dict], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["name", "email", "phone"])
        writer.writeheader()
        writer.writerows(rows)


def build_report(stats: Stats) -> str:
    dropped = stats.read - stats.written
    lines = [
        "Data Cleaning Report",
        "=" * 24,
        f"Rows read           : {stats.read}",
        f"Rows written (clean): {stats.written}",
        f"Rows dropped        : {dropped}",
        "-" * 24,
        f"  duplicates removed: {stats.duplicates}",
        f"  invalid emails    : {stats.invalid_email}",
        f"  missing names     : {stats.missing_name}",
        f"  phones normalized : {stats.phones_normalized}",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Clean, validate and de-duplicate a contact CSV.")
    parser.add_argument("--in", dest="infile", required=True, help="messy input CSV")
    parser.add_argument("--out", default="contacts_clean.csv", help="cleaned output CSV")
    parser.add_argument("--report", default=None, help="optional path to write the report")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(message)s",
        datefmt="%H:%M:%S",
    )

    try:
        rows = read_csv(args.infile)
    except OSError as exc:
        log.error("cannot read %s: %s", args.infile, exc)
        return 1

    stats = Stats()
    cleaned = clean_rows(rows, stats)
    write_csv(cleaned, args.out)

    report = build_report(stats)
    if args.report:
        with open(args.report, "w", encoding="utf-8") as fh:
            fh.write(report + "\n")
    log.info("wrote %d clean rows -> %s", stats.written, args.out)
    print(report)
    return 0 if stats.written else 1


if __name__ == "__main__":
    sys.exit(main())
