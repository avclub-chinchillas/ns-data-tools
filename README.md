# 'Network Survey' Data Processing Tools

Tools to clean, analyze and process data produced by the Android 'Network Survey' application.

## clean-blanks.py

`clean-blanks.py` is a small helper that removes or normalizes empty fields in CSV files produced by the Network Survey app. It can trim whitespace-only cells, convert repeated empty markers to a consistent empty string, and optionally drop entirely blank rows. Use it as a pre-step before running analysis scripts.

Usage example:

```
python3 clean-blanks.py input.csv output.csv
```

## data-cleaner.py

`data-cleaner.py` provides higher-level data normalization and column transformations tailored to Network Survey exports. It removes duplicate entries in a particular column, 'search_column'.

Usage example:

```
python3 data-cleaner.py input.csv search_column
```
Options
- `-o, --output` : Output CSV path (default: input filename with `_cleaned.csv` suffix)
- `-d` : CSV delimiter character, default=','

## resolve-oui.py : Wi-Fi MAC Vendor Resolver for CSV

This small utility reads a CSV file and resolves MAC address vendors using https://api.macvendors.com.

Features
- Read MAC addresses from a named CSV column
- Append vendor names as a new column
- Rate-limited HTTP requests (default 1 request/sec)
- Maximum request cap (default 1000)

Usage

Run the script with the input CSV and the name of the column that contains MAC addresses:

```
python3 resolve-oui.py devices.csv mac
```

Options
- `-o, --output` : Output CSV path (default: input filename with `_vendors.csv` suffix)
- `--vendor-column` : Name of the appended vendor column (default `vendor`)
- `--max-requests` : Maximum number of HTTP requests to send (default `1000`)
- `--rate` : Maximum requests per second (default `1.0`)
- `--timeout` : HTTP timeout in seconds (default `5.0`)
- `--quiet` : Suppress per-row progress output

Example

```
python3 resolve_oui_csv.py devices.csv mac -o devices_with_vendors.csv --max-requests 500 --rate 1.0
```

Notes
- If the input CSV contains more rows than `--max-requests`, rows after the cap will have `vendor=SKIPPED`.
- Empty MAC values produce empty vendor cells.


