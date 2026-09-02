#!/usr/bin/env python3
"""Gate: static web UI calls stream resolve and play APIs."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "static/index.html"


def main() -> int:
    text = INDEX.read_text(encoding="utf-8")
    required = ["/api/stream/resolve", "/api/stream/play", "/api/genres", "/api/watch/continue"]
    missing = [s for s in required if s not in text]
    if missing:
        print("MISSING_WIRING:" + ",".join(missing))
        return 1
    if "exclude_genres" not in text or "genres" not in text:
        print("MISSING_GENRE_PARAMS")
        return 1
    print("WEB_PLAY_WIRING_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
