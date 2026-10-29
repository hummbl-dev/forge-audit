"""Read-only multi-forge inventory comparison and sync-drift detection.

Works on inventories of the form `{repo_name: last_push_iso8601}`. Pure logic
here is unit-testable without network; the CLI shells out to `gh`/`tea`/`glab`
for the actual read-only inventory.
"""

from __future__ import annotations

import json
from typing import Any


def drift(primary: dict[str, str], mirror: dict[str, str]) -> dict[str, Any]:
    """Compare two inventories.

    `primary` is the system of record; `mirror` is the copy. Timestamps are
    compared lexicographically, which is valid for same-format ISO-8601 UTC
    strings (e.g. "2026-10-29T00:02:08Z").
    """
    p, m = set(primary), set(mirror)
    missing_in_mirror = sorted(p - m)
    missing_in_primary = sorted(m - p)
    behind_in_mirror: dict[str, tuple[str, str]] = {}
    for name in p & m:
        if mirror[name] < primary[name]:
            behind_in_mirror[name] = (mirror[name], primary[name])
    return {
        "missing_in_mirror": missing_in_mirror,
        "missing_in_primary": missing_in_primary,
        "behind_in_mirror": behind_in_mirror,
    }


def summarize(d: dict[str, Any]) -> str:
    lines = [
        f"missing_in_mirror={len(d['missing_in_mirror'])} "
        f"missing_in_primary={len(d['missing_in_primary'])} "
        f"behind_in_mirror={len(d['behind_in_mirror'])}"
    ]
    for name in d["missing_in_mirror"]:
        lines.append(f"  MISSING(mirror) {name}")
    for name in d["missing_in_primary"]:
        lines.append(f"  MISSING(primary) {name}")
    for name, (mirror_ts, primary_ts) in sorted(d["behind_in_mirror"].items()):
        lines.append(f"  BEHIND {name} mirror={mirror_ts} primary={primary_ts}")
    return "\n".join(lines)


def load_inventory(path: str) -> dict[str, str]:
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in data.items()):
        raise ValueError("inventory must be a flat {repo: iso8601} object")
    return data
