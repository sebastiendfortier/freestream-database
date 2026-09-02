#!/bin/sh
set -e
cd "$(dirname "$0")/.."
pixi run python scripts/verify_web_genre_filters.py | grep -q WEB_GENRE_FILTERS_OK
pixi run python scripts/verify_web_play_wiring.py | grep -q WEB_PLAY_WIRING_OK
pixi run python scripts/verify_stream_bridge.py | grep -q STREAM_BRIDGE_OK
pixi run python -m pytest tests/ -q
echo ALL_MET
