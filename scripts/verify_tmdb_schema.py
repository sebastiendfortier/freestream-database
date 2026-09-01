#!/usr/bin/env python3
"""Schema proof: sample TMDb fetch + IMDb join."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, cwd=ROOT, check=True)


def main() -> int:
    run([sys.executable, "src/fetch_tmdb_catalog.py", "--pages", "1", "--sample", "50"])
    if not (ROOT / "data" / "imdb_ratings.parquet").exists():
        run([sys.executable, "src/fetch_imdb_ratings.py"])
    run([sys.executable, "src/prepare_view.py"])
    run([sys.executable, "scripts/verify_titles_view.py"])
    print("TMDB_IMDB_SCHEMA_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
