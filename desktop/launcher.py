"""Launch FreeStream web UI in a native PyWebView window."""

from __future__ import annotations

import multiprocessing
import socket
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def _pick_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_for_server(port: int, timeout_s: float = 30.0) -> bool:
    import urllib.error
    import urllib.request

    deadline = time.time() + timeout_s
    url = f"http://127.0.0.1:{port}/api/health"
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status == 200:
                    return True
        except (urllib.error.URLError, TimeoutError):
            time.sleep(0.2)
    return False


def main() -> None:
    multiprocessing.freeze_support()

    import uvicorn
    import webview

    from serve import app

    port = _pick_port()
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="info")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    if not _wait_for_server(port):
        raise SystemExit("FreeStream server failed to start.")

    window = webview.create_window(
        "FreeStream",
        f"http://127.0.0.1:{port}/",
        width=1280,
        height=800,
        min_size=(900, 600),
    )
    webview.start(gui="edgechromium" if sys.platform == "win32" else None, debug=False)
    server.should_exit = True
    thread.join(timeout=5)


if __name__ == "__main__":
    main()
