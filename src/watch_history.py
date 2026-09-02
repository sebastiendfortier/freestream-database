"""Local watch progress storage."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from app_config import watch_history_path

RESUME_THRESHOLD_MS = 5000
FINISHED_RATIO = 0.90


def _default_store() -> dict[str, Any]:
    return {"entries": {}}


def load_store() -> dict[str, Any]:
    history_file = watch_history_path()
    if history_file.exists():
        try:
            data = json.loads(history_file.read_text(encoding="utf-8"))
            if isinstance(data, dict) and isinstance(data.get("entries"), dict):
                return data
        except Exception:
            pass
    return _default_store()


def save_store(store: dict[str, Any]) -> None:
    history_file = watch_history_path()
    history_file.parent.mkdir(parents=True, exist_ok=True)
    tmp = history_file.with_suffix(".json.tmp")
    payload = json.dumps(store, indent=2, ensure_ascii=False)
    tmp.write_text(payload, encoding="utf-8")
    tmp.replace(history_file)


def compute_is_finished(position_ms: int, duration_ms: int) -> bool:
    return duration_ms > 0 and position_ms >= int(duration_ms * FINISHED_RATIO)


def save_progress(
    episode_url: str,
    series_title: str,
    episode_title: str,
    season_number: str,
    episode_number: str,
    poster_url: str,
    position_ms: int,
    duration_ms: int,
    *,
    last_watched_timestamp: int | None = None,
    is_finished: bool | None = None,
) -> dict[str, Any]:
    store = load_store()
    ts = last_watched_timestamp if last_watched_timestamp is not None else int(time.time() * 1000)
    finished = is_finished if is_finished is not None else compute_is_finished(position_ms, duration_ms)
    entry = {
        "episodeUrl": episode_url,
        "seriesTitle": series_title,
        "episodeTitle": episode_title,
        "seasonNumber": season_number,
        "episodeNumber": episode_number,
        "posterUrl": poster_url,
        "positionMs": position_ms,
        "durationMs": duration_ms,
        "lastWatchedTimestamp": ts,
        "isFinished": finished,
    }
    store["entries"][episode_url] = entry
    save_store(store)
    return entry


def list_continue_watching(limit: int = 15) -> list[dict[str, Any]]:
    entries = list(load_store()["entries"].values())
    in_progress = [entry for entry in entries if not entry.get("isFinished")]
    in_progress.sort(key=lambda entry: entry.get("lastWatchedTimestamp", 0), reverse=True)
    return in_progress[:limit]
