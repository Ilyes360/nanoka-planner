"""Résolution des URLs médias (icônes, splash)."""

from __future__ import annotations

from pathlib import Path

from nanoka.paths import CHARACTER_IMAGES, IMAGES, WEAPON_IMAGES


def media_url_from_path(path: Path | None) -> str | None:
    if not path:
        return None
    rel = path.relative_to(IMAGES).as_posix()
    return f"/media/{rel}"


def pick_character_splash_file(folder: Path) -> Path | None:
    hits: list[Path] = []
    for path in folder.glob("*.webp"):
        name = path.name.lower()
        if "ui_gacha_avatarimg_" not in name:
            continue
        if any(x in name for x in ("_p_", "_large", "costume", "side")):
            continue
        if name.endswith("_p.webp"):
            continue
        hits.append(path)
    if hits:
        return sorted(hits)[0]
    return None


def pick_character_avatar_file(folder: Path) -> Path | None:
    avatar_hits: list[Path] = []
    for path in folder.glob("*.webp"):
        name = path.name.lower()
        if "ui_avataricon_" not in name:
            continue
        if "side" in name or "costume" in name:
            continue
        avatar_hits.append(path)
    if avatar_hits:
        return sorted(avatar_hits)[0]
    fallback = sorted(p for p in folder.glob("*.webp") if "ui_avataricon_" in p.name.lower())
    return fallback[0] if fallback else None


def pick_weapon_icon_file(folder: Path) -> Path | None:
    for pattern in ("icon.webp", "*.webp"):
        hits = sorted(folder.glob(pattern))
        if hits:
            return hits[0]
    return None


def pick_weapon_splash_file(folder: Path) -> Path | None:
    card_hits = sorted(folder.glob("card.webp"))
    if card_hits:
        return card_hits[0]
    return None
