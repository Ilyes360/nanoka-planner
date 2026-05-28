"""URLs d'icônes pour matériaux et consommables (catalogue Genshin / Nanoka)."""

from __future__ import annotations

STATIC_GI_ASSETS = "https://static.nanoka.cc/assets/gi"

# Livres d'EXP personnage (IDs jeu standard)
CHARACTER_EXP_BOOK_IDS: dict[str, int] = {
    "Hero's Wit": 104003,
    "Adventurer's Experience": 104002,
    "Wanderer's Advice": 104001,
}

# Minerais d'amélioration d'arme
WEAPON_ORE_IDS: dict[str, int] = {
    "Mystic Enhancement Ore": 104013,
    "Fine Enhancement Ore": 104012,
    "Enhancement Ore": 104011,
}


def static_item_icon_url(item_id: int | str | None) -> str:
    if item_id is None:
        return ""
    sid = str(item_id).strip()
    if not sid.isdigit():
        return ""
    return f"{STATIC_GI_ASSETS}/UI_ItemIcon_{sid}.webp"


def resolve_icon_url(
    *,
    item_id: int | str | None = None,
    name: str = "",
    icon_url: str = "",
) -> str:
    """Préfère l'URL enrichie ; sinon déduit depuis l'ID ou les consommables connus."""
    if icon_url:
        return icon_url
    if item_id is not None:
        url = static_item_icon_url(item_id)
        if url:
            return url
    key = str(name).strip()
    known = CHARACTER_EXP_BOOK_IDS.get(key) or WEAPON_ORE_IDS.get(key)
    if known:
        return static_item_icon_url(known)
    return ""
