from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nanoka.item_icons import resolve_icon_url


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def slim_material(mat: dict) -> dict:
    item = mat.get("item") or {}
    item_id = item.get("item_id") or mat.get("id")
    name = str(mat.get("name", "")).strip()
    return {
        "name": name,
        "count": int(mat.get("count") or 0),
        "item_id": item_id,
        "icon_url": resolve_icon_url(
            item_id=item_id,
            name=name,
            icon_url=str(item.get("icon_url") or ""),
        ),
    }


def merge_material_row(acc: dict[str, dict], mat: dict) -> None:
    name = str(mat.get("name", "")).strip()
    if not name:
        return
    item_id = mat.get("item_id")
    icon_url = resolve_icon_url(
        item_id=item_id,
        name=name,
        icon_url=str(mat.get("icon_url") or ""),
    )
    prev = acc.get(name)
    if prev is None:
        acc[name] = {
            "name": name,
            "count": int(mat.get("count") or 0),
            "item_id": item_id,
            "icon_url": icon_url,
        }
        return
    prev["count"] += int(mat.get("count") or 0)
    if not prev.get("item_id") and item_id:
        prev["item_id"] = item_id
    if not prev.get("icon_url") and icon_url:
        prev["icon_url"] = icon_url


def aggregate_totals(steps: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    totals: dict[str, dict] = {}
    total_mora = 0
    for step in steps:
        total_mora += int(step.get("mora") or 0)
        for mat in step.get("materials") or []:
            if isinstance(mat, dict):
                merge_material_row(totals, mat)
    rows = sorted(totals.values(), key=lambda x: str(x["name"]).lower())
    return rows, total_mora
