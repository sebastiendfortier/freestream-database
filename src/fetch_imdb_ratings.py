#!/usr/bin/env python3
"""Download IMDb title.ratings and store as parquet."""

from __future__ import annotations

import gzip
import io
import sys
from pathlib import Path

import httpx
import polars as pl

SRC = Path(__file__).resolve().parent
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from app_config import imdb_ratings_path

RATINGS_URL = "https://datasets.imdbws.com/title.ratings.tsv.gz"


def download_ratings() -> pl.DataFrame:
    with httpx.Client(timeout=120.0, follow_redirects=True) as client:
        resp = client.get(RATINGS_URL)
        resp.raise_for_status()
        raw = gzip.decompress(resp.content)
    return pl.read_csv(
        io.BytesIO(raw),
        separator="\t",
        infer_schema_length=1000,
    ).rename({"tconst": "imdb_id", "averageRating": "imdb_rating", "numVotes": "imdb_vote_count"})


def main() -> int:
    df = download_ratings()
    out = imdb_ratings_path()
    out.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(out)
    print(f"IMDB_RATINGS_OK rows={df.height}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
