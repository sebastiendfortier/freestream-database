"""FreeStream database paths and settings."""

from __future__ import annotations

import json
import os
from pathlib import Path

APP_NAME = "FreeStream"
APP_VERSION = "0.1.0"

_REPO_ROOT = Path(__file__).resolve().parent.parent
_RESOLVER_CONFIG = _REPO_ROOT.parent / "freestream-resolver" / "config" / "tmdb.json"


def repo_root() -> Path:
    return _REPO_ROOT


def data_dir() -> Path:
    env = os.environ.get("FREESTREAM_DATA_DIR")
    path = Path(env).expanduser() if env else _REPO_ROOT / "data"
    path.mkdir(parents=True, exist_ok=True)
    return path


def titles_raw_path() -> Path:
    return data_dir() / "titles_raw.parquet"


def titles_view_path() -> Path:
    return data_dir() / "titles_view.parquet"


def imdb_ratings_path() -> Path:
    return data_dir() / "imdb_ratings.parquet"


def genre_index_path() -> Path:
    return data_dir() / "genre_index.json"


def static_dir() -> Path:
    return _REPO_ROOT / "static"


def catalog_ready() -> bool:
    return titles_view_path().exists()


def load_tmdb_api_key() -> str:
    if os.environ.get("TMDB_API_KEY"):
        return os.environ["TMDB_API_KEY"].strip()
    if _RESOLVER_CONFIG.is_file():
        data = json.loads(_RESOLVER_CONFIG.read_text(encoding="utf-8"))
        key = (data.get("api_key") or "").strip()
        if key:
            return key
    raise RuntimeError(
        "TMDb API key missing. Run freestream-resolver extract_free99_tmdb_key.py "
        "or set TMDB_API_KEY."
    )
