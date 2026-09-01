#!/usr/bin/env python3
"""Verify stream bridge imports and resolve path."""

from __future__ import annotations

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from stream_bridge import resolve_title  # noqa: E402


def main() -> int:
    streams = resolve_title(
        imdb_id="tt0468569",
        title="The Dark Knight",
        year=2008,
        media_type="movie",
    )
    if not streams:
        print("STREAM_BRIDGE_NO_STREAMS", file=sys.stderr)
        return 1
    if not streams[0].get("streamUrl"):
        print("STREAM_BRIDGE_BAD_PAYLOAD", file=sys.stderr)
        return 1
    print("STREAM_BRIDGE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
