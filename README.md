# FreeStream Database

TMDb browse metadata + IMDb ratings catalog, FastAPI web UI, VLC stream bridge, Windows MSI.

## Setup

```bash
pixi install
pixi run fetch-tmdb --pages 5
pixi run fetch-imdb
pixi run prepare
pixi run serve
```

Desktop app: `pixi run python -m desktop.launcher`

Requires sibling `freestream-resolver` for TMDb key fallback and stream resolution.
