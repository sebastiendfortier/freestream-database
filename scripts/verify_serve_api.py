#!/usr/bin/env python3
"""Smoke test serve API."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from fastapi.testclient import TestClient
from serve import app, load_data


def main() -> int:
    load_data()
    client = TestClient(app)
    health = client.get("/api/health")
    if health.status_code != 200:
        return 1
    titles = client.get("/api/titles?page_size=5")
    if titles.status_code != 200:
        return 1
    body = titles.json()
    if not body.get("catalog_ready"):
        print("Catalog not ready", file=sys.stderr)
        return 1
    if not body.get("rows"):
        print("No rows returned", file=sys.stderr)
        return 1
    print("SERVE_API_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
