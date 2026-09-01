"""Launch VLC with resolved stream URLs."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass

from freestream_resolver.models import ResolvedStream


@dataclass
class PlayResult:
    ok: bool
    quality: str = ""
    pid: int | None = None
    error: str = ""
    command: list[str] | None = None


def get_vlc_executable() -> str:
    vlc_path = shutil.which("vlc") or shutil.which("vlc.exe")
    if vlc_path:
        return vlc_path
    if sys.platform == "win32":
        for candidate in (
            os.path.expandvars(r"%ProgramFiles%\VideoLAN\VLC\vlc.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\VideoLAN\VLC\vlc.exe"),
        ):
            if os.path.isfile(candidate):
                return candidate
    if sys.platform == "darwin":
        mac = "/Applications/VLC.app/Contents/MacOS/VLC"
        if os.path.isfile(mac):
            return mac
    for candidate in ("/usr/bin/vlc", "/usr/local/bin/vlc", "/snap/bin/vlc"):
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    raise FileNotFoundError("VLC executable not found")


def build_vlc_command(
    stream: ResolvedStream,
    *,
    title: str | None = None,
    start_time_s: int = 0,
) -> list[str]:
    cmd = [get_vlc_executable()]
    referrer = stream.headers.get("Referer")
    user_agent = stream.headers.get("User-Agent")
    if referrer:
        cmd.append(f"--http-referrer={referrer}")
    if user_agent:
        cmd.append(f"--http-user-agent={user_agent}")
    if title:
        cmd.append(f"--meta-title={title}")
    if start_time_s > 0:
        cmd.append(f"--start-time={start_time_s}")
    cmd.append("--no-video-title-show")
    cmd.append(stream.stream_url)
    if referrer:
        cmd.append(f":http-referrer={referrer}")
    if user_agent:
        cmd.append(f":http-user-agent={user_agent}")
    return cmd


def play_in_vlc(
    stream: ResolvedStream,
    *,
    title: str | None = None,
    start_time_s: int = 0,
    detach: bool = True,
) -> PlayResult:
    try:
        cmd = build_vlc_command(stream, title=title, start_time_s=start_time_s)
    except FileNotFoundError as err:
        return PlayResult(ok=False, error=str(err))
    try:
        if detach:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                start_new_session=True,
            )
            return PlayResult(ok=True, quality=stream.quality, pid=proc.pid, command=cmd)
        res = subprocess.run(cmd, check=False)
        return PlayResult(ok=res.returncode == 0, quality=stream.quality, command=cmd)
    except Exception as err:
        return PlayResult(ok=False, error=str(err), command=cmd)
