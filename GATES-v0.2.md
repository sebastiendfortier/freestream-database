# Gates: freestream-database v0.2 catalog

OWNS: src/**, data/**, scripts/**, GATES-v0.2.md

Scope: Full TMDb catalog (1000+ titles), TV asset sync

- [x] G1: Catalog has at least 1000 titles
  CHECK: /bin/sh -c 'cd /home/slyfox/Documents/freestream-database && pixi run python scripts/fetch_full_catalog.py && pixi run python scripts/verify_catalog_scale.py'
  EXPECT: CATALOG_SCALE_OK
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/freestream-resolver; exit=0; path=c2fddda5c8ee/25; out=CATALOG_ALREADY_OK rows=3971 | CATALOG_SCALE_OK rows=3971

- [x] G2: titles_view regenerated from full raw catalog
  CHECK: /bin/sh -c 'cd /home/slyfox/Documents/freestream-database && pixi run python scripts/verify_titles_view.py'
  EXPECT: TITLES_VIEW_OK
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/freestream-resolver; exit=0; path=c2fddda5c8ee/25; out=TITLES_VIEW_OK rows=3971

- [x] G3: TV catalog assets synced
  CHECK: /bin/sh -c 'cd /home/slyfox/Documents/freestream-tv && pixi run python tools/sync_catalog_parquet.py'
  EXPECT: CATALOG_SYNC_OK
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/freestream-resolver; exit=0; path=c2fddda5c8ee/25; out=CATALOG_SYNC_OK rows=3971 parquet=0.9MB json.gz=0.8MB poster_https=3971
