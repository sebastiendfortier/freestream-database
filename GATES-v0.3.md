# Gates: freestream-database v0.3

OWNS: src/**, static/**, scripts/**, GATES-v0.3.md

Scope: Web genre filters, play wiring, watch history API

- [x] G1: Genre filter parity with API
  CHECK: /bin/sh -c 'cd /home/slyfox/Documents/freestream-database && pixi run python scripts/verify_web_genre_filters.py'
  EXPECT: WEB_GENRE_FILTERS_OK
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/freestream-database; exit=0; path=00db6cba9506/22; out=WEB_GENRE_FILTERS_OK | /home/slyfox/Documents/freestream-database/.pixi/envs/default/lib/python3.14/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2...

- [x] G2: Web UI wired to stream resolve and play
  CHECK: /bin/sh -c 'cd /home/slyfox/Documents/freestream-database && pixi run python scripts/verify_web_play_wiring.py'
  EXPECT: WEB_PLAY_WIRING_OK
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/freestream-database; exit=0; path=00db6cba9506/22; out=WEB_PLAY_WIRING_OK

- [x] G3: Stream bridge resolves URLs
  CHECK: /bin/sh -c 'cd /home/slyfox/Documents/freestream-database && pixi run python scripts/verify_stream_bridge.py'
  EXPECT: STREAM_BRIDGE_OK
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/freestream-database; exit=0; path=00db6cba9506/22; out=STREAM_BRIDGE_OK

- [x] G4: pytest suite passes
  CHECK: /bin/sh -c 'cd /home/slyfox/Documents/freestream-database && pixi run python -m pytest tests/ -q'
  EXPECT: passed
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/freestream-database; exit=0; path=00db6cba9506/22; out=..                                                                       [100%] | =============================== warnings summary =============================== | .pixi/envs/default/lib/python3.14/site-packages/fastapi/testclient.py:1 |  ...
