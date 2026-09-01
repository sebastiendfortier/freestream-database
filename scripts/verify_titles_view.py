#!/usr/bin/env python3
"""Verify titles_view.parquet schema and row count."""

from __future__ import annotations

import sys
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from app_config import titles_view_path

REQUIRED = {
    "tmdb_id",
    "imdb_id",
    "media_type",
    "title",
    "imdb_rating",
    "imdb_vote_count",
    "genres",
    "poster_cdn",
    "backdrop_cdn",
    "overview",
}


def main() -> int:
    path = titles_view_path()
    if not path.exists():
        print("titles_view.parquet missing", file=sys.stderr)
        return 1
    df = pl.read_parquet(path)
    missing = REQUIRED - set(df.columns)
    if missing:
        print(f"Missing columns: {missing}", file=sys.stderr)
        return 1
    if df.height < 10:
        print(f"Too few rows: {df.height}", file=sys.stderr)
        return 1
    print(f"TITLES_VIEW_OK rows={df.height}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
