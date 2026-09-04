#!/usr/bin/env python3
"""Fill empty TMDb status via detail endpoints (list payloads omit status)."""

from __future__ import annotations

import sys
import time
from datetime import date
from pathlib import Path

import httpx
import polars as pl

SRC = Path(__file__).resolve().parent
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from app_config import load_tmdb_api_key, titles_raw_path, titles_view_path
from prepare_view import build_view, write_genre_index
from app_config import imdb_ratings_path

TMDB_BASE = "https://api.themoviedb.org/3/"


def derive_status_from_date(media_type: str, release_date: str) -> str:
    today = date.today().isoformat()
    if release_date and release_date > today:
        return "Upcoming"
    if (media_type or "").lower() == "movie":
        return "Released"
    return "Ended"


def fetch_status(client: httpx.Client, media_type: str, tmdb_id: int) -> str:
    path = f"{media_type}/{tmdb_id}"
    resp = client.get(
        f"{TMDB_BASE}{path}",
        params={"api_key": load_tmdb_api_key(), "language": "en-US"},
        timeout=30.0,
    )
    resp.raise_for_status()
    return (resp.json().get("status") or "").strip()


def main() -> int:
    raw_path = titles_raw_path()
    if not raw_path.is_file():
        print(f"MISSING {raw_path}", file=sys.stderr)
        return 1

    raw = pl.read_parquet(raw_path)
    rows = raw.to_dicts()
    updated = 0
    failed = 0
    with httpx.Client() as client:
        for i, row in enumerate(rows):
            if (row.get("status") or "").strip():
                continue
            media = (row.get("media_type") or "movie").lower()
            tid = int(row["tmdb_id"])
            try:
                status = fetch_status(client, media, tid)
            except httpx.HTTPError:
                status = ""
                failed += 1
            if not status:
                status = derive_status_from_date(media, row.get("release_date") or "")
            row["status"] = status
            updated += 1
            if updated % 50 == 0:
                print(f"progress updated={updated} failed={failed} i={i}", flush=True)
            time.sleep(0.04)

    out = pl.DataFrame(rows)
    out.write_parquet(raw_path)
    print(f"RAW_STATUS_OK rows={out.height} updated={updated} failed={failed}")

    ratings = pl.read_parquet(imdb_ratings_path())
    view = build_view(out, ratings)
    view.write_parquet(titles_view_path())
    write_genre_index(view)
    print(f"VIEW_STATUS_OK rows={view.height}")
    print(view["status"].value_counts())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
