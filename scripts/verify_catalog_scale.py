#!/usr/bin/env python3
"""Verify catalog has minimum title count."""

from __future__ import annotations

import sys
from pathlib import Path

import polars as pl

MIN_ROWS = 1000
ROOT = Path(__file__).resolve().parents[1]
VIEW = ROOT / "data" / "titles_view.parquet"


def main() -> int:
    if not VIEW.is_file():
        print(f"MISSING: {VIEW}", file=sys.stderr)
        return 1
    rows = pl.read_parquet(VIEW).height
    if rows < MIN_ROWS:
        print(f"CATALOG_TOO_SMALL rows={rows} need>={MIN_ROWS}", file=sys.stderr)
        return 1
    print(f"CATALOG_SCALE_OK rows={rows}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
