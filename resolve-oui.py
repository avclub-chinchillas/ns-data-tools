#!/usr/bin/env python3
"""Resolve MAC vendor names for MAC addresses stored in a CSV file.

This script reads an input CSV file, looks up vendor names from https://api.macvendors.com/$MAC
for a specified MAC column, and writes an output CSV with a new column containing the vendor.

It respects a maximum number of requests (default 1000) and a maximum rate (default 1 req/sec).
"""
from __future__ import annotations

import argparse
import csv
import sys
import time
import logging
from typing import Optional

import requests


def lookup_vendor(mac: str, timeout: float = 5.0, retries: int = 2) -> Optional[str]:
    """Query api.macvendors.com for the given MAC address.

    Returns the vendor string on success, or None if not found or on repeated errors.
    """
    url = f"https://api.macvendors.com/{mac}"
    backoff = 0.5
    for attempt in range(1, retries + 2):
        try:
            resp = requests.get(url, timeout=timeout)
            if resp.status_code == 200:
                return resp.text.strip()
            if resp.status_code == 404:
                return "NOT FOUND"
            # for other statuses, we will retry
            logging.debug("macvendors returned %s for %s", resp.status_code, mac)
        except requests.RequestException as e:
            logging.debug("request exception for %s: %s", mac, e)

        # retry with backoff
        if attempt <= retries:
            time.sleep(backoff)
            backoff *= 2

    return None


def process_csv(input_path: str, output_path: str, mac_column: str, vendor_column: str = "vendor",
                max_requests: int = 1000, rate: float = 1.0, timeout: float = 5.0) -> None:
    """Read input CSV, resolve vendors (rate-limited), and write results to output CSV.

    - input_path: path to input CSV (must have header)
    - output_path: path to write result CSV
    - mac_column: name of the column that contains MAC addresses
    - vendor_column: name of the vendor column to append
    - max_requests: maximum number of requests to send
    - rate: requests per second (e.g., 1.0 = max 1/sec)
    - timeout: HTTP request timeout in seconds
    """
    interval = 1.0 / float(rate) if rate > 0 else 0.0
    requests_sent = 0

    with open(input_path, newline="", encoding="utf-8") as inf, \
            open(output_path, "w", newline="", encoding="utf-8") as outf:
        reader = csv.DictReader(inf)
        if mac_column not in reader.fieldnames:
            raise SystemExit(f"MAC column '{mac_column}' not found in input CSV headers: {reader.fieldnames}")

        fieldnames = list(reader.fieldnames) + [vendor_column]
        writer = csv.DictWriter(outf, fieldnames=fieldnames)
        writer.writeheader()

        # next_allowed is used to enforce rate limit
        next_allowed = time.monotonic()

        for row in reader:
            vendor = ""
            mac = (row.get(mac_column) or "").strip()

            if mac and requests_sent < max_requests:
                now = time.monotonic()
                if now < next_allowed:
                    time.sleep(next_allowed - now)

                vendor = lookup_vendor(mac, timeout=timeout)
                requests_sent += 1
                next_allowed = time.monotonic() + interval

                # normalize None -> empty string
                if vendor is None:
                    vendor = ""

            elif not mac:
                vendor = ""
            else:
                vendor = "SKIPPED"

            row[vendor_column] = vendor
            writer.writerow(row)

            # simple progress to stderr
            sys.stderr.write(f"Processed row, MAC={mac!s}, vendor={vendor!s}\n")
            sys.stderr.flush()

    logging.info("Done: %d requests sent", requests_sent)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Resolve MAC vendor names from a CSV column using api.macvendors.com")
    p.add_argument("input_csv", help="Input CSV path (must include header)")
    p.add_argument("mac_column", help="Name of the CSV column that contains MAC addresses")
    p.add_argument("-o", "--output", help="Output CSV path (default: input with _vendors.csv suffix)")
    p.add_argument("--vendor-column", default="vendor", help="Name of the vendor column to append (default: vendor)")
    p.add_argument("--max-requests", type=int, default=1000, help="Maximum number of HTTP requests to send (default 1000)")
    p.add_argument("--rate", type=float, default=1.0, help="Maximum requests per second (default 1.0)")
    p.add_argument("--timeout", type=float, default=5.0, help="HTTP timeout in seconds (default 5.0)")
    p.add_argument("--quiet", action="store_true", help="Do not print per-row progress to stderr")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    if args.output:
        output_path = args.output
    else:
        if args.input_csv.lower().endswith('.csv'):
            output_path = args.input_csv[:-4] + '_vendors.csv'
        else:
            output_path = args.input_csv + '_vendors.csv'

    if args.quiet:
        # redirect stderr to /dev/null to silence per-row messages
        sys.stderr = open('/dev/null', 'w')

    try:
        process_csv(args.input_csv, output_path, args.mac_column, vendor_column=args.vendor_column,
                    max_requests=args.max_requests, rate=args.rate, timeout=args.timeout)
    except SystemExit as e:
        # argparse or other explicit SystemExit messages
        print(str(e), file=sys.stderr)
        raise
    except Exception as e:
        logging.exception("Error processing CSV: %s", e)
        raise


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    main()
