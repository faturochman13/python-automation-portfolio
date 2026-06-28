# Contact Data Cleaner — Python Automation Sample

A small, **production-style** automation that turns a messy contact export into a
clean, validated, de-duplicated CSV — plus a report of exactly what it changed.
This is the "automate the boring spreadsheet work" task clients pay for.

> Input is a synthetic `contacts_messy.csv` (mixed casing, stray whitespace,
> duplicate rows, invalid emails, mixed phone formats). No real personal data.

## What it demonstrates

| Quality clients ask for | How this script does it |
|---|---|
| **Data validation** | Regex email check; rows with bad/missing data are dropped, not silently kept |
| **De-duplication** | Case-insensitive email key; keeps the first occurrence |
| **Normalization** | Title-cases names, lowercases emails, standardizes phone digits |
| **Transparency** | Prints a report: rows read / written / dropped, with a breakdown |
| **Observability** | Structured logging (`-v` for debug) |
| **Configurable** | CLI flags for input, output, and optional report file |

## Usage

```bash
python data_cleaner.py --in contacts_messy.csv --out contacts_clean.csv --report report.txt
```

## Example run

```
Data Cleaning Report
========================
Rows read           : 10
Rows written (clean): 5
Rows dropped        : 5
------------------------
  duplicates removed: 2
  invalid emails    : 2
  missing names     : 1
  phones normalized : 5
```

Before → after (one row):

```
"  john   SMITH ", "John.Smith@Example.com ", "+1 (415) 555-0132"
   ->  "John Smith", "john.smith@example.com", "+14155550132"
```

## What I can build for you

This extends to **Excel/Google Sheets cleanup**, CRM imports, deduplicating large
lists, merging data from multiple sources, scheduled batch jobs, and validation
pipelines. Standard library only — no heavy dependencies. Send me a sample file
and I'll scope it.
