#!/usr/bin/env python3
"""Serve searchable titles from titles_view.parquet."""

from __future__ import annotations

import json
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import polars as pl
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

SRC = Path(__file__).resolve().parent
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from app_config import catalog_ready, genre_index_path, static_dir, titles_view_path
from stream_bridge import play_stream, resolve_title

_df: pl.DataFrame | None = None
_genres: list[str] = []


def load_data() -> None:
    global _df, _genres
    path = titles_view_path()
    if not path.exists():
        _df = None
        _genres = []
        return
    _df = pl.read_parquet(path)
    gpath = genre_index_path()
    _genres = json.loads(gpath.read_text(encoding="utf-8")) if gpath.exists() else []


@asynccontextmanager
async def lifespan(_: FastAPI):
    if catalog_ready():
        load_data()
    yield


app = FastAPI(title="FreeStream Database", lifespan=lifespan)
STATIC = static_dir()
if STATIC.is_dir():
    app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/genres")
def list_genres() -> dict:
    return {"genres": _genres, "count": len(_genres)}


@app.get("/api/types")
def list_types() -> dict:
    return {"types": ["MOVIE", "TV"]}


@app.get("/api/statuses")
def list_statuses() -> dict:
    return {"statuses": ["airing", "ended"]}


@app.get("/api/titles")
def query_titles(
    min_score: float | None = None,
    min_year: int | None = None,
    status: str | None = None,
    type: str | None = None,
    genres: list[str] = Query(default=[]),
    exclude_genres: list[str] = Query(default=[]),
    search: str = "",
    sort: str = "imdb_rating",
    order: str = "desc",
    page: int = 1,
    page_size: int = 60,
) -> dict:
    if _df is None:
        return {
            "total": 0,
            "page": 1,
            "page_size": page_size,
            "pages": 0,
            "rows": [],
            "catalog_ready": False,
        }

    df = _df
    if min_score is not None:
        df = df.filter(pl.col("imdb_rating") >= min_score)
    if min_year is not None:
        df = df.filter(pl.col("year") >= min_year)
    if type and type.strip().upper() not in ("", "ALL"):
        df = df.filter(pl.col("media_type") == type.strip().lower())
    if status and status.strip().lower() not in ("", "all"):
        st = status.strip().lower()
        if st == "airing":
            df = df.filter(pl.col("status").str.to_lowercase().str.contains("returning"))
        elif st == "ended":
            df = df.filter(
                pl.col("status").str.to_lowercase().str.contains("ended")
                | pl.col("status").str.to_lowercase().str.contains("canceled")
            )

    for genre in genres:
        g = genre.strip().lower()
        if g:
            df = df.filter(pl.col("genres").list.eval(pl.element().str.to_lowercase() == g).list.any())
    for genre in exclude_genres:
        g = genre.strip().lower()
        if g:
            df = df.filter(~pl.col("genres").list.eval(pl.element().str.to_lowercase() == g).list.any())

    if search.strip():
        term = search.strip().lower()
        df = df.filter(
            pl.col("title").str.to_lowercase().str.contains(term, literal=False)
            | pl.col("original_title").str.to_lowercase().str.contains(term, literal=False)
            | pl.col("overview").str.to_lowercase().str.contains(term, literal=False)
            | pl.col("genres_csv").str.to_lowercase().str.contains(term, literal=False)
        )

    allowed = {"title", "year", "imdb_rating", "media_type"}
    sort_col = sort if sort in allowed else "imdb_rating"
    descending = order.lower() != "asc"
    df = df.sort(sort_col, descending=descending, nulls_last=True)

    total = df.height
    page = max(1, page)
    page_size = min(max(1, page_size), 200)
    offset = (page - 1) * page_size
    page_df = df.slice(offset, page_size)

    rows = []
    for row in page_df.iter_rows(named=True):
        rows.append(
            {
                "tmdbId": row["tmdb_id"],
                "imdbId": row["imdb_id"],
                "title": row["title"],
                "mediaType": row["media_type"].upper(),
                "year": row["year"],
                "imdbRating": row["imdb_rating"],
                "poster": row["poster_cdn"],
                "fallbackImage": row["backdrop_cdn"],
                "genres": row["genres"],
                "overview": row["overview"],
                "status": row["status"],
            }
        )

    pages = (total + page_size - 1) // page_size if page_size else 0
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
        "rows": rows,
        "catalog_ready": True,
    }


@app.get("/api/health")
def health() -> dict:
    return {"catalog_ready": catalog_ready(), "rows": _df.height if _df is not None else 0}


@app.get("/api/stream/resolve")
def stream_resolve(
    imdb_id: str,
    title: str,
    media_type: str = "movie",
    year: int | None = None,
    season: int | None = None,
    episode: int | None = None,
    flare: bool = False,
) -> dict:
    streams = resolve_title(
        imdb_id=imdb_id,
        title=title,
        media_type=media_type,
        year=year,
        season=season,
        episode=episode,
        use_flare=flare,
    )
    return {"streams": streams, "count": len(streams)}


@app.post("/api/stream/play")
def stream_play(body: dict) -> dict:
    stream_url = (body.get("streamUrl") or body.get("stream_url") or "").strip()
    if not stream_url:
        return {"ok": False, "error": "Missing streamUrl"}
    return play_stream(
        stream_url,
        quality=body.get("quality") or "SD",
        headers=body.get("headers") or {},
        title=body.get("title"),
        provider=body.get("provider") or "",
        source_url=body.get("sourceUrl") or body.get("source_url") or "",
    )
