from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def slim_material(mat: dict) -> dict:
    item = mat.get("item") or {}
    return {
        "name": mat.get("name", ""),
        "count": int(mat.get("count") or 0),
        "item_id": item.get("item_id") or mat.get("id"),
        "icon_url": item.get("icon_url", ""),
    }


def aggregate_totals(steps: list[dict[str, Any]]) -> tuple[list[dict[str, int | str]], int]:
    totals: dict[str, int] = {}
    total_mora = 0
    for step in steps:
        total_mora += int(step.get("mora") or 0)
        for mat in step.get("materials") or []:
            name = str(mat.get("name", "")).strip()
            if not name:
                continue
            totals[name] = totals.get(name, 0) + int(mat.get("count") or 0)
    return (
        [{"name": n, "count": c} for n, c in sorted(totals.items(), key=lambda x: x[0].lower())],
        total_mora,
    )
