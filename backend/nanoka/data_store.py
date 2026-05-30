"""Caches en mémoire pour JSON et index médias (évite relectures disque répétées)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from nanoka.paths import (
    CHARACTER_IMAGES,
    CHARACTER_LOADOUTS_JSON,
    CHARACTERS_JSON,
    WEAPON_IMAGES,
    WEAPON_LOADOUTS_JSON,
    WEAPONS_JSON,
)
from nanoka.report_common import load_json

_JSON_CACHE: dict[str, dict[str, Any]] = {}
_LOADOUT_INDEX: dict[str, dict[str, dict[str, Any]]] = {}
_MEDIA_INDEX: dict[str, dict[str, dict[str, str | None]]] = {}
_CHARACTER_PROFILES: dict[str, Any] | None = None
_WEAPON_PROFILES: dict[str, Any] | None = None
_LEVEL_EXP_INDEX: dict[str, Any] | None = None
_WEAPON_LEVEL_EXP_INDEX: dict[str, Any] | None = None


def clear_caches() -> None:
    _JSON_CACHE.clear()
    _LOADOUT_INDEX.clear()
    _MEDIA_INDEX.clear()
    global _CHARACTER_PROFILES, _WEAPON_PROFILES, _LEVEL_EXP_INDEX, _WEAPON_LEVEL_EXP_INDEX
    _CHARACTER_PROFILES = None
    _WEAPON_PROFILES = None
    _LEVEL_EXP_INDEX = None
    _WEAPON_LEVEL_EXP_INDEX = None


def _mtime(path: Path) -> float:
    return path.stat().st_mtime if path.is_file() else 0.0


def _cached_list(path: Path) -> list[dict[str, Any]]:
    key = str(path.resolve())
    mt = _mtime(path)
    entry = _JSON_CACHE.get(key)
    if entry and entry["mtime"] == mt:
        return entry["data"]
    data = load_json(path) if path.is_file() else []
    rows = data if isinstance(data, list) else []
    _JSON_CACHE[key] = {"mtime": mt, "data": rows}
    return rows


def _loadout_index(kind: str, path: Path) -> dict[str, dict[str, Any]]:
    key = f"{kind}:{path.resolve()}"
    mt = _mtime(path)
    entry = _LOADOUT_INDEX.get(key)
    if entry and entry["mtime"] == mt:
        return entry["data"]
    by_id = {str(row.get("id", "")): row for row in _cached_list(path) if isinstance(row, dict)}
    _LOADOUT_INDEX[key] = {"mtime": mt, "data": by_id}
    return by_id


def character_loadouts() -> list[dict[str, Any]]:
    return _cached_list(CHARACTER_LOADOUTS_JSON)


def weapon_loadouts() -> list[dict[str, Any]]:
    return _cached_list(WEAPON_LOADOUTS_JSON)


def character_loadout(entity_id: str) -> dict[str, Any] | None:
    return _loadout_index("character", CHARACTER_LOADOUTS_JSON).get(entity_id)


def weapon_loadout(entity_id: str) -> dict[str, Any] | None:
    return _loadout_index("weapon", WEAPON_LOADOUTS_JSON).get(entity_id)


def _entity_id_from_url(url: str, kind: str) -> str:
    marker = f"/{kind}/"
    if marker not in (url or ""):
        return ""
    return (url or "").split(marker)[-1].split("/")[0].strip()


def _build_media_index(kind: str) -> dict[str, dict[str, str | None]]:
    from nanoka.media import (
        media_url_from_path,
        pick_character_avatar_file,
        pick_character_splash_file,
        pick_weapon_icon_file,
        pick_weapon_splash_file,
    )

    base = CHARACTER_IMAGES if kind == "character" else WEAPON_IMAGES
    index: dict[str, dict[str, str | None]] = {}
    if not base.is_dir():
        return index
    for folder in base.iterdir():
        if not folder.is_dir():
            continue
        eid = folder.name.split("_", 1)[0]
        if not eid.isdigit():
            continue
        if kind == "character":
            index[eid] = {
                "icon_url": media_url_from_path(pick_character_avatar_file(folder)),
                "splash_url": media_url_from_path(pick_character_splash_file(folder)),
            }
        else:
            index[eid] = {
                "icon_url": media_url_from_path(pick_weapon_icon_file(folder)),
                "splash_url": media_url_from_path(pick_weapon_splash_file(folder)),
            }
    return index


def media_for(kind: str, entity_id: str) -> dict[str, str | None]:
    if kind not in _MEDIA_INDEX:
        _MEDIA_INDEX[kind] = _build_media_index(kind)
    return _MEDIA_INDEX[kind].get(
        entity_id,
        {"icon_url": None, "splash_url": None},
    )


def level_exp_index() -> dict[str, list[int]]:
    global _LEVEL_EXP_INDEX
    mt = _mtime(CHARACTERS_JSON)
    if _LEVEL_EXP_INDEX is not None and _LEVEL_EXP_INDEX["mtime"] == mt:
        return _LEVEL_EXP_INDEX["data"]

    from nanoka import ascension_report

    rows = _cached_list(CHARACTERS_JSON)
    data = ascension_report.index_level_exp_by_id(rows)
    _LEVEL_EXP_INDEX = {"mtime": mt, "data": data}
    return data


def weapon_level_exp_index() -> dict[str, list[int]]:
    global _WEAPON_LEVEL_EXP_INDEX
    mt = _mtime(WEAPONS_JSON)
    if _WEAPON_LEVEL_EXP_INDEX is not None and _WEAPON_LEVEL_EXP_INDEX["mtime"] == mt:
        return _WEAPON_LEVEL_EXP_INDEX["data"]

    from nanoka import weapon_report

    rows = _cached_list(WEAPONS_JSON)
    data = weapon_report.index_weapon_level_exp(rows)
    _WEAPON_LEVEL_EXP_INDEX = {"mtime": mt, "data": data}
    return data


def character_profiles() -> dict[str, dict[str, str]]:
    global _CHARACTER_PROFILES
    mt = _mtime(CHARACTERS_JSON)
    if _CHARACTER_PROFILES is not None and _CHARACTER_PROFILES["mtime"] == mt:
        return _CHARACTER_PROFILES["data"]

    from nanoka.labels import REGION_LABELS, character_rarity_label, weapon_type_label

    index: dict[str, dict[str, str]] = {}
    for row in _cached_list(CHARACTERS_JSON):
        if not isinstance(row, dict):
            continue
        eid = _entity_id_from_url(str(row.get("url", "")), "character")
        if not eid:
            continue
        raw = row.get("raw_data") or {}
        info = raw.get("chara_info") or {}
        region_key = str(info.get("region") or "")
        index[eid] = {
            "description": str(raw.get("desc") or info.get("detail") or "").strip(),
            "title": str(info.get("title") or "").strip(),
            "vision": str(info.get("vision") or "").strip(),
            "element": str(raw.get("element") or "").strip(),
            "weapon_type": weapon_type_label(str(raw.get("weapon") or "")),
            "rarity": character_rarity_label(raw.get("rarity")),
            "region": REGION_LABELS.get(region_key, region_key.replace("ASSOC_TYPE_", "").title()),
            "constellation": str(info.get("constellation") or "").strip(),
        }
    _CHARACTER_PROFILES = {"mtime": mt, "data": index}
    return index


def weapon_profiles() -> dict[str, dict[str, str]]:
    global _WEAPON_PROFILES
    mt = _mtime(WEAPONS_JSON)
    if _WEAPON_PROFILES is not None and _WEAPON_PROFILES["mtime"] == mt:
        return _WEAPON_PROFILES["data"]

    from nanoka.labels import rarity_label, weapon_type_label

    index: dict[str, dict[str, str]] = {}
    for row in _cached_list(WEAPONS_JSON):
        if not isinstance(row, dict):
            continue
        eid = _entity_id_from_url(str(row.get("url", "")), "weapon")
        if not eid:
            continue
        raw = row.get("raw_data") or {}
        index[eid] = {
            "description": str(raw.get("desc") or "").strip(),
            "weapon_type": weapon_type_label(str(raw.get("weapon_type") or "")),
            "rarity": rarity_label(raw.get("rarity")),
        }
    _WEAPON_PROFILES = {"mtime": mt, "data": index}
    return index
