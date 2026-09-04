"""Bridge catalog titles to freestream-resolver and VLC."""

from __future__ import annotations

import os
import sys
from typing import Any

import httpx

from freestream_resolver.hoster_resolve import resolve_candidate
from freestream_resolver.http_client import KODI_UA
from freestream_resolver.models import ResolvedStream, ScrapeRequest, StreamCandidate
from freestream_resolver.orchestrator import collect_candidates, resolve_request
from freestream_resolver.sites.levidia import LevidiaScraper

from stream_proxy import register_upstream, should_proxy
from vlc_player import PlayResult, play_in_vlc


def _cdn_default_headers(stream_url: str) -> dict[str, str]:
    lower = stream_url.lower()
    if any(token in lower for token in ("wootly", "nebula.to", "jabroni.mov", "luluvdo", "dood")):
        return {
            "User-Agent": KODI_UA,
            "Referer": "https://web.wootly.ch/",
            "Origin": "https://web.wootly.ch",
        }
    return {"User-Agent": KODI_UA}


def _merge_play_headers(stream_url: str, headers: dict[str, str] | None) -> dict[str, str]:
    merged = _cdn_default_headers(stream_url)
    merged.update(headers or {})
    if not merged.get("Referer") and "Referer" in _cdn_default_headers(stream_url):
        merged["Referer"] = _cdn_default_headers(stream_url)["Referer"]
    return merged


def _is_direct_media(url: str) -> bool:
    lower = url.lower()
    return any(ext in lower for ext in (".m3u8", ".mp4", ".webm"))


def _ensure_playable_url(
    stream_url: str,
    *,
    headers: dict[str, str] | None = None,
    provider: str = "",
) -> tuple[str, dict[str, str]] | None:
    if _is_direct_media(stream_url):
        return stream_url, headers or {}
    lower = stream_url.lower()
    if not any(token in lower for token in ("go.php", "wootly", "luluvdo", "dood", "vide0.net")):
        return stream_url, headers or {}
    with httpx.Client(timeout=90.0, follow_redirects=True) as client:
        resolved = resolve_candidate(
            client,
            StreamCandidate(url=stream_url, provider=provider, headers=headers or {}),
        )
    if not resolved or not _is_direct_media(resolved.stream_url):
        return None
    merged = dict(headers or {})
    merged.update(resolved.headers or {})
    return resolved.stream_url, merged


def _streams_payload(streams: list[ResolvedStream]) -> list[dict[str, Any]]:
    return [
        {
            "streamUrl": s.stream_url,
            "quality": s.quality,
            "headers": s.headers,
            "provider": s.provider,
            "sourceUrl": s.source_url,
            "contentType": s.content_type or "video/mp4",
        }
        for s in streams
    ]


def resolve_title(
    *,
    imdb_id: str,
    title: str,
    media_type: str = "movie",
    year: int | None = None,
    season: int | None = None,
    episode: int | None = None,
    use_flare: bool = False,
) -> list[dict[str, Any]]:
    req = ScrapeRequest(
        imdb_id=imdb_id,
        title=title,
        year=year,
        media_type=media_type.lower(),
        season=season,
        episode=episode,
    )
    resolved = resolve_request(req, use_flare=use_flare)
    if resolved:
        return _streams_payload(resolved)

    # Hoster resolve may fail while scrape still found embed URLs — expose those for VLC/yt-dlp retry.
    candidates = collect_candidates(req)
    playable = [
        c for c in candidates if c.url and "go.php" not in c.url.lower()
    ]
    if playable:
        with httpx.Client(timeout=90.0, follow_redirects=True) as client:
            from freestream_resolver.hoster_resolve import resolve_all

            resolved_candidates = resolve_all(client, playable)
            if resolved_candidates:
                return _streams_payload(resolved_candidates)

    return [
        {
            "streamUrl": c.url,
            "quality": c.quality,
            "headers": c.headers,
            "provider": c.provider or "scrape",
            "sourceUrl": c.url,
            "contentType": "video/mp4",
            "direct": c.direct,
        }
        for c in candidates
        if c.url and "go.php" not in c.url.lower()
    ]


def list_tv_episodes(
    *,
    title: str,
    year: int | None = None,
    season: int = 1,
) -> list[dict[str, str | int]]:
    req = ScrapeRequest(
        imdb_id="",
        title=title,
        year=year,
        media_type="tv",
        season=season,
    )
    scraper = LevidiaScraper()
    try:
        return scraper.list_episodes(req)
    finally:
        scraper.close()


def list_available_seasons(
    *,
    title: str,
    year: int | None = None,
    max_season: int = 12,
) -> list[int]:
    seasons: list[int] = []
    for season in range(1, max_season + 1):
        episodes = list_tv_episodes(title=title, year=year, season=season)
        if not episodes:
            break
        seasons.append(season)
    return seasons


def _should_use_proxy(stream_url: str) -> bool:
    mode = os.environ.get("FREESTREAM_USE_PROXY", "auto").lower()
    if mode == "never":
        return False
    if mode == "always":
        return should_proxy(stream_url)
    # Pipe MRL works on Linux/macOS VLC; Windows needs the local proxy.
    if sys.platform != "win32":
        return False
    return should_proxy(stream_url)


def play_stream(
    stream_url: str,
    *,
    quality: str = "SD",
    headers: dict[str, str] | None = None,
    title: str | None = None,
    provider: str = "",
    source_url: str = "",
) -> dict[str, Any]:
    playable = _ensure_playable_url(
        stream_url,
        headers=headers,
        provider=provider,
    )
    if not playable:
        return {
            "ok": False,
            "quality": quality,
            "pid": None,
            "error": "Could not resolve stream to a playable URL",
        }
    stream_url, headers = playable
    headers = _merge_play_headers(stream_url, headers)
    vlc_url = stream_url
    vlc_headers = headers
    if _should_use_proxy(stream_url):
        vlc_url = register_upstream(stream_url, headers)
        vlc_headers = {}
    stream = ResolvedStream(
        stream_url=vlc_url,
        quality=quality,
        headers=vlc_headers,
        provider=provider,
        source_url=source_url or stream_url,
    )
    result: PlayResult = play_in_vlc(stream, title=title, detach=True)
    return {
        "ok": result.ok,
        "quality": result.quality,
        "pid": result.pid,
        "error": result.error,
    }


def play_title(
    *,
    imdb_id: str,
    title: str,
    media_type: str = "movie",
    year: int | None = None,
    season: int | None = None,
    episode: int | None = None,
    use_flare: bool = False,
) -> dict[str, Any]:
    streams = resolve_title(
        imdb_id=imdb_id,
        title=title,
        media_type=media_type,
        year=year,
        season=season,
        episode=episode,
        use_flare=use_flare,
    )
    if not streams:
        return {"ok": False, "error": "No stream found for this title"}

    last_error = "Could not launch VLC"
    for stream in streams[:5]:
        result = play_stream(
            stream["streamUrl"],
            quality=stream.get("quality") or "SD",
            headers=stream.get("headers") or {},
            title=title,
            provider=stream.get("provider") or "",
            source_url=stream.get("sourceUrl") or stream.get("source_url") or "",
        )
        if result.get("ok"):
            result["provider"] = stream.get("provider") or ""
            return result
        last_error = result.get("error") or last_error
    return {"ok": False, "error": last_error}
