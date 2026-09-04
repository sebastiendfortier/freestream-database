# Gates: freestream-web watch modal family parity

OWNS: freestream-database/static/index.html, src/serve.py, src/stream_bridge.py, src/watch_history.py, GATES-web-watch-parity.md

Scope: anime-web modal-watch layout — season chips, episode rows, resume/watched; no Sub/Dub.

- [x] G1: Season chips + episode list + resume/watched markup in index.html
  CHECK: /bin/sh -c 'python3 -c "from pathlib import Path; t=Path(\"/home/slyfox/Documents/freestream-database/static/index.html\").read_text(); assert \"season-chip\" in t; assert \"episode-status\" in t; assert \"resume-hero-btn\" in t; assert \"Sub (\" not in t; print(\"WEB_WATCH_UI_OK\")"'
  EXPECT: WEB_WATCH_UI_OK
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/anime-tv; exit=0; path=c2fddda5c8ee/25; out=WEB_WATCH_UI_OK

- [x] G2: /api/stream/seasons and /api/watch/series endpoints exist
  CHECK: /bin/sh -c 'python3 -c "from pathlib import Path; s=Path(\"/home/slyfox/Documents/freestream-database/src/serve.py\").read_text(); assert \"/api/stream/seasons\" in s; assert \"/api/watch/series\" in s; assert \"list_available_seasons\" in s; assert \"list_series_history\" in s; print(\"WEB_WATCH_API_OK\")"'
  EXPECT: WEB_WATCH_API_OK
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/anime-tv; exit=0; path=c2fddda5c8ee/25; out=WEB_WATCH_API_OK

- [x] G3: SPECS-family-parity.md documents web + TV contracts
  CHECK: /bin/sh -c 'python3 -c "from pathlib import Path; t=Path(\"/home/slyfox/Documents/freestream-tv/SPECS-family-parity.md\").read_text(); assert \"Season chips\" in t; assert \"No Sub/Dub\" in t; assert \"freestream-database\" in t; print(\"SPECS_OK\")"'
  EXPECT: SPECS_OK
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/anime-tv; exit=0; path=c2fddda5c8ee/25; out=SPECS_OK
