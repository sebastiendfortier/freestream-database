#!/usr/bin/env python3
"""Fetch full catalog if below scale threshold."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[1]
VIEW = ROOT / "data" / "titles_view.parquet"
MIN_ROWS = 1000
PAGES = 40


def main() -> int:
    rows = 0
    if VIEW.is_file():
        rows = pl.read_parquet(VIEW).height
    if rows >= MIN_ROWS:
        print(f"CATALOG_ALREADY_OK rows={rows}")
        return 0

    steps = [
        ["pixi", "run", "python", "src/fetch_tmdb_catalog.py", "--pages", str(PAGES)],
        ["pixi", "run", "python", "src/fetch_imdb_ratings.py"],
        ["pixi", "run", "python", "src/prepare_view.py"],
    ]
    for cmd in steps:
        print(f"RUN {' '.join(cmd)}", flush=True)
        subprocess.run(cmd, cwd=ROOT, check=True)

    rows = pl.read_parquet(VIEW).height
    if rows < MIN_ROWS:
        print(f"CATALOG_FETCH_INSUFFICIENT rows={rows}", file=sys.stderr)
        return 1
    print(f"CATALOG_FETCH_OK rows={rows}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
