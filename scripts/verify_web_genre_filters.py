#!/usr/bin/env python3
"""Gate: /api/titles genre filters match parquet logic for fixtures."""

from __future__ import annotations

import sys
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from app_config import titles_view_path  # noqa: E402

FIXTURES = [
    {"genres": ["Action"], "exclude_genres": []},
    {"genres": ["Drama"], "exclude_genres": ["Horror"]},
    {"genres": ["Comedy", "Romance"], "exclude_genres": ["Documentary"]},
]


def filter_df(df: pl.DataFrame, genres: list[str], exclude_genres: list[str]) -> pl.DataFrame:
    out = df
    for genre in genres:
        g = genre.strip().lower()
        if g:
            out = out.filter(pl.col("genres").list.eval(pl.element().str.to_lowercase() == g).list.any())
    for genre in exclude_genres:
        g = genre.strip().lower()
        if g:
            out = out.filter(~pl.col("genres").list.eval(pl.element().str.to_lowercase() == g).list.any())
    return out


def main() -> int:
    path = titles_view_path()
    if not path.exists():
        print("CATALOG_MISSING")
        return 1
    df = pl.read_parquet(path)
    from fastapi.testclient import TestClient
    from serve import app, load_data

    load_data()
    with TestClient(app) as client:
        for fixture in FIXTURES:
            expected = filter_df(df, fixture["genres"], fixture["exclude_genres"]).height
            params: list[tuple[str, str]] = []
            for g in fixture["genres"]:
                params.append(("genres", g))
            for g in fixture["exclude_genres"]:
                params.append(("exclude_genres", g))
            resp = client.get("/api/titles", params=params + [("page_size", "1")])
            actual = resp.json().get("total", -1)
            if actual != expected:
                print(
                    f"MISMATCH genres={fixture['genres']} exclude={fixture['exclude_genres']} "
                    f"expected={expected} actual={actual}"
                )
                return 1
    print("WEB_GENRE_FILTERS_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
