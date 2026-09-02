# Gates: freestream-database v0.3

OWNS: src/**, static/**, scripts/**, GATES-v0.3.md

Scope: Web genre filters, play wiring, watch history API

- [ ] G1: Genre filter parity with API
  CHECK: /bin/sh -c 'cd /home/slyfox/Documents/freestream-database && pixi run python scripts/verify_web_genre_filters.py'
  EXPECT: WEB_GENRE_FILTERS_OK
  EVIDENCE: pending

- [ ] G2: Web UI wired to stream resolve and play
  CHECK: /bin/sh -c 'cd /home/slyfox/Documents/freestream-database && pixi run python scripts/verify_web_play_wiring.py'
  EXPECT: WEB_PLAY_WIRING_OK
  EVIDENCE: pending

- [ ] G3: Stream bridge resolves URLs
  CHECK: /bin/sh -c 'cd /home/slyfox/Documents/freestream-database && pixi run python scripts/verify_stream_bridge.py'
  EXPECT: STREAM_BRIDGE_OK
  EVIDENCE: pending

- [ ] G4: pytest suite passes
  CHECK: /bin/sh -c 'cd /home/slyfox/Documents/freestream-database && pixi run python -m pytest tests/ -q'
  EXPECT: passed
  EVIDENCE: pending
