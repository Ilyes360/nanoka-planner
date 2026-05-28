"""API HTTP pour le frontend Nanoka."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.gzip import GZipMiddleware

from nanoka import ascension_report, data_store, talent_report, weapon_report
from nanoka.paths import (
    CHARACTER_ASCENSION_REPORT_JSON,
    CHARACTER_LOADOUTS_JSON,
    CHARACTER_TALENT_REPORT_JSON,
    WEAPON_ASCENSION_REPORT_JSON,
    WEAPON_LOADOUTS_JSON,
    IMAGES,
)

app = FastAPI(title="Nanoka Planner API", version="1.0.0")

app.add_middleware(GZipMiddleware, minimum_size=500)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if IMAGES.is_dir():
    app.mount("/media", StaticFiles(directory=str(IMAGES)), name="media")


def _is_displayable(row: dict[str, Any]) -> bool:
    """Exclut les entrees dont le scrape a echoue (nom de secours Unknown)."""
    return str(row.get("name", "")).strip().lower() != "unknown"


def _list_summary(kind: str, row: dict[str, Any]) -> dict[str, Any]:
    eid = str(row.get("id", ""))
    media = data_store.media_for(kind, eid)
    return {
        "id": eid,
        "name": row.get("name", ""),
        "url": row.get("url", ""),
        "icon_url": media.get("icon_url"),
    }


def _detail_summary(kind: str, row: dict[str, Any]) -> dict[str, Any]:
    eid = str(row.get("id", ""))
    media = data_store.media_for(kind, eid)
    return {
        "id": eid,
        "name": row.get("name", ""),
        "url": row.get("url", ""),
        "icon_url": media.get("icon_url"),
        "splash_url": media.get("splash_url") if kind == "character" else None,
    }


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/characters")
def list_characters() -> list[dict[str, Any]]:
    visible = [r for r in data_store.character_loadouts() if isinstance(r, dict) and _is_displayable(r)]
    return sorted([_list_summary("character", r) for r in visible], key=lambda x: x["name"].lower())


@app.get("/api/characters/{entity_id}")
def get_character(
    entity_id: str,
    talent_levels: str | None = None,
) -> dict[str, Any]:
    loadout = data_store.character_loadout(entity_id)
    if not loadout or not _is_displayable(loadout):
        raise HTTPException(status_code=404, detail="Character not found")

    level_exp_index = data_store.level_exp_index()
    ascension = ascension_report.build_character_report(loadout, level_exp_index)
    talents = talent_report.build_talent_report(loadout)
    profile = data_store.character_profiles().get(entity_id, {})

    out: dict[str, Any] = {
        **_detail_summary("character", loadout),
        **profile,
        "ascension": ascension,
        "talents": talents,
    }
    if talent_levels:
        levels_map = talent_report.parse_talent_levels_param(talent_levels, talents)
        if levels_map:
            out["talents_plan"] = talent_report.aggregate_talent_report_with_levels(talents, levels_map)
    return out


@app.get("/api/weapons")
def list_weapons() -> list[dict[str, Any]]:
    visible = [r for r in data_store.weapon_loadouts() if isinstance(r, dict) and _is_displayable(r)]
    return sorted([_list_summary("weapon", r) for r in visible], key=lambda x: x["name"].lower())


@app.get("/api/weapons/{entity_id}")
def get_weapon(entity_id: str) -> dict[str, Any]:
    loadout = data_store.weapon_loadout(entity_id)
    if not loadout or not _is_displayable(loadout):
        raise HTTPException(status_code=404, detail="Weapon not found")

    level_exp_index = data_store.weapon_level_exp_index()
    ascension = weapon_report.build_weapon_report(loadout, level_exp_index)
    profile = data_store.weapon_profiles().get(entity_id, {})

    return {
        **_detail_summary("weapon", loadout),
        **profile,
        "ascension": ascension,
    }


@app.get("/api/meta/reports")
def reports_meta() -> dict[str, Any]:
    """Indique si les rapports JSON pre-genere existent sur disque."""
    return {
        "character_ascension": CHARACTER_ASCENSION_REPORT_JSON.is_file(),
        "character_talents": CHARACTER_TALENT_REPORT_JSON.is_file(),
        "weapon_ascension": WEAPON_ASCENSION_REPORT_JSON.is_file(),
        "character_loadouts": CHARACTER_LOADOUTS_JSON.is_file(),
        "weapon_loadouts": WEAPON_LOADOUTS_JSON.is_file(),
    }

