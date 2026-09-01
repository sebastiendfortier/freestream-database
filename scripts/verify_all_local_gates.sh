#!/bin/sh
set -e
cd "$(dirname "$0")/.."
pixi run python scripts/verify_tmdb_schema.py | grep -q TMDB_IMDB_SCHEMA_OK
pixi run python scripts/verify_titles_view.py | grep -q TITLES_VIEW_OK
pixi run python scripts/verify_serve_api.py | grep -q SERVE_API_OK
pixi run python -m pytest tests/ -q
pixi run python scripts/verify_stream_bridge.py | grep -q STREAM_BRIDGE_OK
pixi run python scripts/verify_desktop_launcher.py | grep -q DESKTOP_LAUNCHER_OK
python3 -c "import tomllib; d=tomllib.load(open('pyproject.toml','rb')); assert 'pyappdist' in d.get('tool',{}); print('PYAPPDIST_OK')" | grep -q PYAPPDIST_OK
echo ALL_MET
