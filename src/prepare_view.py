#!/usr/bin/env python3
"""Build titles_view.parquet with IMDb ratings join."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import polars as pl

SRC = Path(__file__).resolve().parent
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from app_config import genre_index_path, imdb_ratings_path, titles_raw_path, titles_view_path

GENRE_NAMES = {
    28: "Action",
    12: "Adventure",
    16: "Animation",
    35: "Comedy",
    80: "Crime",
    99: "Documentary",
    18: "Drama",
    10751: "Family",
    14: "Fantasy",
    36: "History",
    27: "Horror",
    10402: "Music",
    9648: "Mystery",
    10749: "Romance",
    878: "Science Fiction",
    10770: "TV Movie",
    53: "Thriller",
    10752: "War",
    37: "Western",
    10759: "Action & Adventure",
    10762: "Kids",
    10763: "News",
    10764: "Reality",
    10765: "Sci-Fi & Fantasy",
    10766: "Soap",
    10767: "Talk",
    10768: "War & Politics",
}


def map_genres(genres: list) -> list[str]:
    out: list[str] = []
    for g in genres:
        if isinstance(g, str) and not g.isdigit():
            out.append(g)
        else:
            try:
                name = GENRE_NAMES.get(int(g))
                if name:
                    out.append(name)
            except (TypeError, ValueError):
                pass
    return sorted(set(out))


def build_view(raw: pl.DataFrame, ratings: pl.DataFrame) -> pl.DataFrame:
    df = raw.with_columns(
        pl.col("genres").map_elements(map_genres, return_dtype=pl.List(pl.Utf8)).alias("genres"),
    )
    df = df.join(ratings, on="imdb_id", how="left")
    df = df.with_columns(
        pl.col("genres").list.join(", ").alias("genres_csv"),
        pl.col("imdb_rating").cast(pl.Float64),
        pl.col("imdb_vote_count").cast(pl.Int64),
    )

    complete = df.filter(
        pl.col("tmdb_id").is_not_null()
        & pl.col("imdb_id").is_not_null()
        & (pl.col("imdb_id") != "")
        & pl.col("imdb_rating").is_not_null()
        & (pl.col("genres").list.len() > 0)
        & (pl.col("overview").str.len_chars() > 0)
        & (
            (pl.col("poster_cdn").str.len_chars() > 0)
            | (pl.col("backdrop_cdn").str.len_chars() > 0)
        )
    )

    view = (
        complete.sort(["imdb_rating", "imdb_vote_count", "year"], descending=[True, True, True])
        .unique(subset=["tmdb_id"], keep="first")
    )
    return view


def write_genre_index(view: pl.DataFrame) -> None:
    counts: dict[str, int] = {}
    for row in view.iter_rows(named=True):
        for g in row.get("genres") or []:
            counts[g] = counts.get(g, 0) + 1
    tags = sorted(counts.keys(), key=lambda k: (-counts[k], k.lower()))
    genre_index_path().write_text(json.dumps(tags, indent=2), encoding="utf-8")


def main() -> int:
    raw_path = titles_raw_path()
    ratings_path = imdb_ratings_path()
    if not raw_path.exists():
        print("Missing titles_raw.parquet — run fetch_tmdb_catalog.py", file=sys.stderr)
        return 1
    if not ratings_path.exists():
        print("Missing imdb_ratings.parquet — run fetch_imdb_ratings.py", file=sys.stderr)
        return 1

    raw = pl.read_parquet(raw_path)
    ratings = pl.read_parquet(ratings_path)
    view = build_view(raw, ratings)
    out = titles_view_path()
    view.write_parquet(out)
    write_genre_index(view)
    print(f"TITLES_VIEW_OK rows={view.height}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
