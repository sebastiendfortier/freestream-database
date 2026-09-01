"""Bridge catalog titles to freestream-resolver and VLC."""

from __future__ import annotations

from typing import Any

from freestream_resolver.models import ResolvedStream, ScrapeRequest
from freestream_resolver.orchestrator import collect_candidates, resolve_request

from vlc_player import PlayResult, play_in_vlc


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
        if c.url
    ]


def play_stream(
    stream_url: str,
    *,
    quality: str = "SD",
    headers: dict[str, str] | None = None,
    title: str | None = None,
    provider: str = "",
    source_url: str = "",
) -> dict[str, Any]:
    stream = ResolvedStream(
        stream_url=stream_url,
        quality=quality,
        headers=headers or {},
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
