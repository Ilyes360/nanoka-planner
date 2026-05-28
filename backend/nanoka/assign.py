from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from nanoka.weapon_exp import parse_level_exp
from nanoka.paths import (
    CHARACTER_ITEMS_JSON,
    CHARACTER_LOADOUTS_JSON,
    CHARACTERS_JSON,
    ITEMS_JSON,
    WEAPON_ITEMS_JSON,
    WEAPON_LOADOUTS_JSON,
    WEAPONS_JSON,
    ensure_data_dirs,
)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def entity_id(url: str, kind: str) -> str:
    match = re.search(rf"/{kind}/(\d+)/?", url or "")
    return match.group(1) if match else ""


def item_id_from_url(url: str) -> int | None:
    match = re.search(r"/item/(\d+)/?", url or "")
    return int(match.group(1)) if match else None


def build_item_lookup(items: list[dict]) -> tuple[dict[int, dict], dict[str, dict]]:
    by_id: dict[int, dict] = {}
    by_name: dict[str, dict] = {}
    for row in items:
        iid = item_id_from_url(row.get("url", ""))
        if iid is not None:
            by_id[iid] = row
        name = str(row.get("name", "")).strip().lower()
        if name and name not in by_name:
            by_name[name] = row
    return by_id, by_name


def item_summary(row: dict | None, mat_id: int | None = None) -> dict:
    if not row:
        return {"item_id": mat_id, "matched": False}
    iid = item_id_from_url(row.get("url", "")) or mat_id
    raw = row.get("raw_data") or {}
    images = row.get("item_images") or []
    icon_url = images[0].get("url", "") if images else ""
    if not icon_url and raw.get("icon"):
        icon_url = f"https://static.nanoka.cc/assets/gi/{raw['icon']}.webp"
    return {
        "item_id": iid,
        "matched": True,
        "name": row.get("name", ""),
        "url": row.get("url", ""),
        "icon_url": icon_url,
        "item_type": raw.get("item_type", "") or row.get("item_category", ""),
        "material_type": raw.get("material_type", ""),
        "rank": raw.get("rank"),
        "source_list": row.get("item_sources") or raw.get("source_list") or [],
    }


def resolve_item(mat: dict, by_id: dict[int, dict], by_name: dict[str, dict]) -> dict | None:
    mid = mat.get("id")
    if isinstance(mid, int) and mid in by_id:
        return by_id[mid]
    if isinstance(mid, str) and mid.isdigit() and int(mid) in by_id:
        return by_id[int(mid)]
    name = str(mat.get("name", "")).strip().lower()
    return by_name.get(name) if name else None


def enrich_mat(mat: dict, by_id: dict[int, dict], by_name: dict[str, dict]) -> dict:
    out = dict(mat)
    mid = mat.get("id")
    if isinstance(mid, str) and mid.isdigit():
        mid = int(mid)
    row = resolve_item(mat, by_id, by_name)
    out["item"] = item_summary(row, mid if isinstance(mid, int) else None)
    return out


def enrich_step(step: dict, by_id: dict[int, dict], by_name: dict[str, dict]) -> dict:
    mats = step.get("mats", [])
    return {
        **{k: v for k, v in step.items() if k != "mats"},
        "materials": [enrich_mat(m, by_id, by_name) for m in mats if isinstance(m, dict)],
    }


def character_loadout(char: dict, by_id: dict[int, dict], by_name: dict[str, dict]) -> dict:
    materials = (char.get("raw_data") or {}).get("materials") or {}
    ascensions = []
    for phase, step in enumerate(materials.get("ascensions") or [], start=1):
        if isinstance(step, dict):
            ascensions.append({"phase": phase, **enrich_step(step, by_id, by_name)})
    talents = []
    for track_idx, track in enumerate(materials.get("talents") or [], start=1):
        if not isinstance(track, list):
            continue
        levels = []
        for level_idx, step in enumerate(track, start=1):
            if isinstance(step, dict):
                levels.append({"level": level_idx, **enrich_step(step, by_id, by_name)})
        talents.append({"track": track_idx, "levels": levels})
    level_exp = (char.get("raw_data") or {}).get("level_exp") or []
    return {
        "name": char.get("name", ""),
        "id": entity_id(char.get("url", ""), "character"),
        "url": char.get("url", ""),
        "level_exp": level_exp if isinstance(level_exp, list) else [],
        "ascensions": ascensions,
        "talents": talents,
    }


def weapon_loadout(weapon: dict, by_id: dict[int, dict], by_name: dict[str, dict]) -> dict:
    raw = weapon.get("raw_data") or {}
    materials = raw.get("materials") or {}
    level_exp = parse_level_exp(raw)
    phases = []
    if isinstance(materials, dict):
        for key, step in sorted(materials.items(), key=lambda x: int(x[0]) if str(x[0]).isdigit() else x[0]):
            if isinstance(step, dict):
                phases.append({"phase": int(key) if str(key).isdigit() else key, **enrich_step(step, by_id, by_name)})
    return {
        "name": weapon.get("name", ""),
        "id": entity_id(weapon.get("url", ""), "weapon"),
        "url": weapon.get("url", ""),
        "level_exp": level_exp if level_exp else [],
        "ascensions": phases,
    }


def iter_mats_from_entity(entity: dict, field: str) -> list[dict]:
    raw = entity.get("raw_data") or {}
    materials = raw.get("materials") or {}
    found: list[dict] = []
    if field == "ascension":
        for step in materials.get("ascensions") or []:
            if isinstance(step, dict):
                found.extend(step.get("mats") or [])
        for track in materials.get("talents") or []:
            if not isinstance(track, list):
                continue
            for step in track:
                if isinstance(step, dict):
                    found.extend(step.get("mats") or [])
    elif field == "weapon_ascension" and isinstance(materials, dict):
        for step in materials.values():
            if isinstance(step, dict):
                found.extend(step.get("mats") or [])
    return [m for m in found if isinstance(m, dict) and str(m.get("name", "")).strip()]


def build_usage_index(
    entities: list[dict],
    entity_type: str,
    by_id: dict[int, dict],
    by_name: dict[str, dict],
) -> list[dict]:
    index: dict[str, dict] = {}

    def touch(mat: dict, entity: dict) -> None:
        name = str(mat.get("name", "")).strip()
        if not name:
            return
        key = name.lower()
        if key not in index:
            index[key] = {
                "name": name,
                "item": item_summary(resolve_item(mat, by_id, by_name), mat.get("id")),
                "seen_quantities": [],
                "used_by": [],
            }
        qty = str(mat.get("count", ""))
        if qty and qty not in index[key]["seen_quantities"]:
            index[key]["seen_quantities"].append(qty)
        ref = {
            "type": entity_type,
            "name": entity.get("name", ""),
            "id": entity_id(entity.get("url", ""), entity_type),
            "url": entity.get("url", ""),
        }
        if ref not in index[key]["used_by"]:
            index[key]["used_by"].append(ref)

    for entity in entities:
        for mat in iter_mats_from_entity(entity, "ascension" if entity_type == "character" else "weapon_ascension"):
            touch(mat, entity)

    return sorted(index.values(), key=lambda x: x["name"].lower())


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Link ascension materials to items and build loadout JSON.")
    p.add_argument("--characters", type=Path, default=CHARACTERS_JSON)
    p.add_argument("--weapons", type=Path, default=WEAPONS_JSON)
    p.add_argument("--items", type=Path, default=ITEMS_JSON)
    p.add_argument("--character-loadouts-out", type=Path, default=CHARACTER_LOADOUTS_JSON)
    p.add_argument("--weapon-loadouts-out", type=Path, default=WEAPON_LOADOUTS_JSON)
    p.add_argument("--character-items-out", type=Path, default=CHARACTER_ITEMS_JSON)
    p.add_argument("--weapon-items-out", type=Path, default=WEAPON_ITEMS_JSON)
    return p.parse_args()


def main() -> None:
    ensure_data_dirs()
    args = parse_args()
    characters = load_json(args.characters)
    weapons = load_json(args.weapons)
    items = load_json(args.items)
    by_id, by_name = build_item_lookup(items)

    char_loadouts = [character_loadout(c, by_id, by_name) for c in characters]
    weapon_loadouts = [weapon_loadout(w, by_id, by_name) for w in weapons]
    char_items = build_usage_index(characters, "character", by_id, by_name)
    weapon_items = build_usage_index(weapons, "weapon", by_id, by_name)

    write_json(args.character_loadouts_out, char_loadouts)
    write_json(args.weapon_loadouts_out, weapon_loadouts)
    write_json(args.character_items_out, char_items)
    write_json(args.weapon_items_out, weapon_items)

    matched = sum(1 for row in char_items if row.get("item", {}).get("matched"))
    print(f"Characters: {len(characters)} -> {args.character_loadouts_out}")
    print(f"Weapons: {len(weapons)} -> {args.weapon_loadouts_out}")
    print(f"Character materials: {len(char_items)} ({matched} matched to item catalog)")
    print(f"Weapon materials: {len(weapon_items)}")
    print(f"Updated: {args.character_items_out.resolve()}")
    print(f"Updated: {args.weapon_items_out.resolve()}")


if __name__ == "__main__":
    main()
