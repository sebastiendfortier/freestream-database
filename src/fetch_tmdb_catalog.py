#!/usr/bin/env python3
"""Fetch movie/TV metadata from TMDb discover lists."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import httpx
import polars as pl

SRC = Path(__file__).resolve().parent
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from app_config import load_tmdb_api_key, titles_raw_path

TMDB_BASE = "https://api.themoviedb.org/3/"
IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
BACKDROP_BASE = "https://image.tmdb.org/t/p/w780"

LISTS = [
    ("movie", "movie/popular"),
    ("movie", "movie/top_rated"),
    ("movie", "movie/now_playing"),
    ("movie", "trending/movie/week"),
    ("tv", "tv/popular"),
    ("tv", "tv/top_rated"),
    ("tv", "tv/on_the_air"),
    ("tv", "trending/tv/week"),
]


def fetch_page(client: httpx.Client, endpoint: str, page: int) -> list[dict]:
    resp = client.get(
        f"{TMDB_BASE}{endpoint}",
        params={"api_key": load_tmdb_api_key(), "page": page, "language": "en-US"},
        timeout=30.0,
    )
    resp.raise_for_status()
    return resp.json().get("results") or []


def external_ids(client: httpx.Client, media_type: str, tmdb_id: int) -> str:
    path = f"{media_type}/{tmdb_id}/external_ids"
    resp = client.get(
        f"{TMDB_BASE}{path}",
        params={"api_key": load_tmdb_api_key()},
        timeout=30.0,
    )
    resp.raise_for_status()
    return (resp.json().get("imdb_id") or "").strip()


def row_from_item(item: dict, media_type: str, imdb_id: str) -> dict:
    title = item.get("title") or item.get("name") or ""
    original = item.get("original_title") or item.get("original_name") or title
    date = item.get("release_date") or item.get("first_air_date") or ""
    year = int(date[:4]) if len(date) >= 4 and date[:4].isdigit() else None
    poster = item.get("poster_path") or ""
    backdrop = item.get("backdrop_path") or ""
    genres = [g.get("name") for g in item.get("genres", []) if g.get("name")]
    if not genres and item.get("genre_ids"):
        genres = [str(g) for g in item["genre_ids"]]
    return {
        "tmdb_id": int(item["id"]),
        "imdb_id": imdb_id,
        "media_type": media_type,
        "title": title,
        "original_title": original,
        "year": year,
        "release_date": date,
        "genres": genres,
        "status": item.get("status") or "",
        "poster_path": poster,
        "backdrop_path": backdrop,
        "poster_cdn": f"{IMAGE_BASE}{poster}" if poster else "",
        "backdrop_cdn": f"{BACKDROP_BASE}{backdrop}" if backdrop else "",
        "overview": (item.get("overview") or "").strip(),
        "runtime": item.get("runtime"),
        "number_of_seasons": item.get("number_of_seasons"),
    }


def fetch_all(max_pages: int = 5) -> pl.DataFrame:
    rows: dict[int, dict] = {}
    with httpx.Client() as client:
        for media_type, endpoint in LISTS:
            for page in range(1, max_pages + 1):
                try:
                    results = fetch_page(client, endpoint, page)
                except httpx.HTTPError as exc:
                    print(f"WARN {endpoint} p{page}: {exc}", file=sys.stderr)
                    break
                if not results:
                    break
                for item in results:
                    tid = int(item["id"])
                    if tid in rows:
                        continue
                    try:
                        imdb = external_ids(client, media_type, tid)
                    except httpx.HTTPError:
                        imdb = ""
                    rows[tid] = row_from_item(item, media_type, imdb)
                    time.sleep(0.05)
                time.sleep(0.25)
    return pl.DataFrame(list(rows.values())) if rows else pl.DataFrame()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages", type=int, default=5)
    parser.add_argument("--sample", type=int, default=0, help="Limit rows for schema proof")
    args = parser.parse_args()

    df = fetch_all(max_pages=args.pages)
    if args.sample > 0:
        df = df.head(args.sample)

    out = titles_raw_path()
    out.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(out)
    print(f"Wrote {df.height} rows to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
