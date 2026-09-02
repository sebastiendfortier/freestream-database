#!/bin/sh
set -e
cd "$(dirname "$0")/.."
pixi run python scripts/fetch_full_catalog.py 2>/dev/null || true
pixi run python scripts/verify_catalog_scale.py | grep -q CATALOG_SCALE_OK
pixi run python scripts/verify_titles_view.py | grep -q TITLES_VIEW_OK
cd ../freestream-tv && pixi run python tools/sync_catalog_parquet.py | grep -q CATALOG_SYNC_OK
echo ALL_MET
