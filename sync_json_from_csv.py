"""One-time script: rebuild daily_market_capitalization.json from daily_market_capitalization.csv.

Reads every row of the CSV and overwrites the JSON so both files contain the
identical dataset. Numeric-looking values are converted back to numbers so the
JSON matches the shape of the original API responses.

The CSV has two row layouts: 18 columns (matching the header) up to 2025-12-18,
and 19 columns from 2025-12-19 onward, when the CSE API added a logo path at
position 3 without the header being rewritten.
"""

import csv
import json

CSV_FILE = "daily_market_capitalization.csv"
JSON_FILE = "daily_market_capitalization.json"

# Columns that must stay as strings even if a value happens to look numeric
STRING_COLUMNS = {"name", "symbol", "logo", "issueDate", "lastTradedTime", "date_scraped"}

LOGO_COLUMN_INDEX = 3


def convert_value(key, value):
    if value is None or value == "":
        return None
    if key in STRING_COLUMNS:
        return value
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        return value


def main():
    records = []
    with open(CSV_FILE, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = [col.strip() for col in next(reader)]
        header_with_logo = header[:LOGO_COLUMN_INDEX] + ["logo"] + header[LOGO_COLUMN_INDEX:]

        for line_num, row in enumerate(reader, start=2):
            if row and row[0] == "id":  # stray header row appended mid-file
                continue
            if len(row) == len(header):
                # Pre-logo row: insert an empty logo so every record has 19 keys
                row = row[:LOGO_COLUMN_INDEX] + [""] + row[LOGO_COLUMN_INDEX:]
            elif len(row) != len(header_with_logo):
                raise ValueError(f"Line {line_num}: unexpected field count {len(row)}")
            records.append({k: convert_value(k, v) for k, v in zip(header_with_logo, row)})

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(records)} records from {CSV_FILE} to {JSON_FILE}")


if __name__ == "__main__":
    main()
