# Gates: freestream-database local

OWNS: src/**, static/**, scripts/**, tests/**, data/**, GATES-local.md

Scope: TMDb/IMDb catalog pipeline, web API, stream bridge, desktop launcher

- [x] G1: TMDb + IMDb schema proof pipeline
  CHECK: /bin/sh -c 'cd /home/slyfox/Documents/freestream-database && pixi run python scripts/verify_tmdb_schema.py'
  EXPECT: TMDB_IMDB_SCHEMA_OK
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/freestream-resolver; exit=0; path=c2fddda5c8ee/25; out=Wrote 50 rows to /home/slyfox/Documents/freestream-database/data/titles_raw.parquet | TITLES_VIEW_OK rows=49 | TITLES_VIEW_OK rows=49 | TMDB_IMDB_SCHEMA_OK

- [x] G2: titles_view parquet valid
  CHECK: /bin/sh -c 'cd /home/slyfox/Documents/freestream-database && pixi run python scripts/verify_titles_view.py'
  EXPECT: TITLES_VIEW_OK
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/freestream-resolver; exit=0; path=c2fddda5c8ee/25; out=TITLES_VIEW_OK rows=49

- [x] G3: FastAPI serve smoke test
  CHECK: /bin/sh -c 'cd /home/slyfox/Documents/freestream-database && pixi run python scripts/verify_serve_api.py'
  EXPECT: SERVE_API_OK
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/freestream-resolver; exit=0; path=c2fddda5c8ee/25; out=SERVE_API_OK | /home/slyfox/Documents/freestream-database/.pixi/envs/default/lib/python3.14/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instea...

- [x] G4: pytest suite
  CHECK: /bin/sh -c 'cd /home/slyfox/Documents/freestream-database && pixi run python -m pytest tests/ -q'
  EXPECT: passed
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/freestream-resolver; exit=0; path=c2fddda5c8ee/25; out=..                                                                       [100%] | =============================== warnings summary =============================== | .pixi/envs/default/lib/python3.14/site-packages/fastapi/testclient.py:1 |  ...

- [x] G5: Stream bridge resolves playable URL
  CHECK: /bin/sh -c 'cd /home/slyfox/Documents/freestream-database && pixi run python scripts/verify_stream_bridge.py'
  EXPECT: STREAM_BRIDGE_OK
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/freestream-resolver; exit=0; path=c2fddda5c8ee/25; out=STREAM_BRIDGE_OK

- [x] G6: Desktop launcher module present
  CHECK: /bin/sh -c 'cd /home/slyfox/Documents/freestream-database && pixi run python scripts/verify_desktop_launcher.py'
  EXPECT: DESKTOP_LAUNCHER_OK
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/freestream-resolver; exit=0; path=c2fddda5c8ee/25; out=DESKTOP_LAUNCHER_OK

- [x] G7: pyappdist MSI config present
  CHECK: /bin/sh -c 'cd /home/slyfox/Documents/freestream-database && python3 -c "import tomllib; d=tomllib.load(open(\"pyproject.toml\",\"rb\")); assert \"pyappdist\" in d.get(\"tool\",{}); print(\"PYAPPDIST_OK\")"'
  EXPECT: PYAPPDIST_OK
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/freestream-resolver; exit=0; path=c2fddda5c8ee/25; out=PYAPPDIST_OK
