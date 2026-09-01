#!/usr/bin/env python3
"""Verify desktop launcher module is importable."""

from __future__ import annotations

import importlib.util
from pathlib import Path


def main() -> int:
    path = Path(__file__).resolve().parents[1] / "desktop" / "launcher.py"
    spec = importlib.util.spec_from_file_location("freestream_desktop_launcher", path)
    if spec is None or spec.loader is None:
        print("DESKTOP_LAUNCHER_MISSING")
        return 1
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not callable(getattr(mod, "main", None)):
        print("DESKTOP_LAUNCHER_NO_MAIN")
        return 1
    print("DESKTOP_LAUNCHER_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
