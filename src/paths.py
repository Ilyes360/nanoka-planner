"""Chemins par défaut du projet."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DATA = ROOT / "data"
RAW = DATA / "raw"
PROCESSED = DATA / "processed"
IMAGES = DATA / "images"
CHARACTER_IMAGES = IMAGES / "characters"
WEAPON_IMAGES = IMAGES / "weapons"
ITEM_IMAGES = IMAGES / "items"

CHARACTERS_JSON = RAW / "characters_nanoka.json"
WEAPONS_JSON = RAW / "weapons_nanoka.json"
ITEMS_JSON = RAW / "items_nanoka.json"

CHARACTER_ITEMS_JSON = PROCESSED / "character_items_nanoka.json"
WEAPON_ITEMS_JSON = PROCESSED / "weapon_items_nanoka.json"
CHARACTER_LOADOUTS_JSON = PROCESSED / "character_loadouts.json"
WEAPON_LOADOUTS_JSON = PROCESSED / "weapon_loadouts.json"
CHARACTER_ASCENSION_REPORT_JSON = PROCESSED / "character_ascension_materials.json"

LEGACY_IMAGE_DIRS: dict[str, Path] = {
    "downloaded_character_images": CHARACTER_IMAGES,
    "downloaded_weapon_images": WEAPON_IMAGES,
    "downloaded_item_images": ITEM_IMAGES,
}


def ensure_data_dirs() -> None:
    for path in (RAW, PROCESSED, CHARACTER_IMAGES, WEAPON_IMAGES, ITEM_IMAGES):
        path.mkdir(parents=True, exist_ok=True)


def relative_to_root(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path).replace("\\", "/")
