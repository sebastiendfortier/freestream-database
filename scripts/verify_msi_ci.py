#!/usr/bin/env python3
"""Gate: GitHub Actions Windows MSI workflow succeeded with artifact."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = "build-windows.yml"
ARTIFACT = "freestream-database-windows-msi"


def run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, cwd=ROOT, text=True).strip()


def main() -> int:
    try:
        runs_json = run(
            [
                "gh",
                "run",
                "list",
                "--workflow",
                WORKFLOW,
                "--limit",
                "5",
                "--json",
                "databaseId,status,conclusion,headBranch,event",
            ]
        )
    except subprocess.CalledProcessError as err:
        print(f"GH_RUN_LIST_FAILED:{err}")
        return 1

    runs = json.loads(runs_json)
    success = next((r for r in runs if r.get("conclusion") == "success"), None)
    if not success:
        print("MSI_CI_NOT_GREEN")
        return 1

    run_id = str(success["databaseId"])
    try:
        names_json = run(
            [
                "gh",
                "api",
                f"repos/sebastiendfortier/freestream-database/actions/runs/{run_id}/artifacts",
                "--jq",
                ".artifacts[].name",
            ]
        )
    except subprocess.CalledProcessError as err:
        print(f"GH_ARTIFACTS_FAILED:{err}")
        return 1

    names = [line.strip() for line in names_json.splitlines() if line.strip()]
    if ARTIFACT not in names:
        print(f"MSI_ARTIFACT_MISSING:{names}")
        return 1

    print("MSI_CI_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
