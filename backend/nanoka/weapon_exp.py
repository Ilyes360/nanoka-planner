"""Calcul des minerais d'experience arme a partir de la courbe level_exp."""

from __future__ import annotations

from typing import TypedDict

from nanoka.exp_books import exp_for_level_range
from nanoka.item_icons import WEAPON_ORE_IDS, resolve_icon_url


class EnhancementOreDef(TypedDict):
    name: str
    exp: int
    item_id: int


# Valeurs standard Genshin Impact
WEAPON_ENHANCEMENT_ORES: list[EnhancementOreDef] = [
    {"name": "Mystic Enhancement Ore", "exp": 10_000, "item_id": WEAPON_ORE_IDS["Mystic Enhancement Ore"]},
    {"name": "Fine Enhancement Ore", "exp": 2_000, "item_id": WEAPON_ORE_IDS["Fine Enhancement Ore"]},
    {"name": "Enhancement Ore", "exp": 400, "item_id": WEAPON_ORE_IDS["Enhancement Ore"]},
]


def parse_level_exp(source: dict) -> list[int]:
    """Courbe arme : level_exp embarque ou xp_requirements (Nanoka)."""
    embedded = source.get("level_exp")
    if isinstance(embedded, list) and embedded:
        return [int(x) for x in embedded]
    xp = source.get("xp_requirements")
    if isinstance(xp, dict) and xp:
        keys = sorted(int(k) for k in xp if str(k).isdigit())
        if keys:
            return [int(xp[str(k)]) for k in keys]
    return []


def ores_for_exp(total_exp: int) -> dict:
    """Repartit l'EXP en minerais d'amelioration (glouton, du plus grand au plus petit)."""
    if total_exp <= 0:
        return {
            "total_exp": 0,
            "ores": [],
            "ore_count": 0,
            "remainder_exp": 0,
        }
    remaining = total_exp
    ores_out: list[dict] = []
    ore_count = 0
    for ore in WEAPON_ENHANCEMENT_ORES:
        count = remaining // ore["exp"]
        if count:
            ores_out.append(
                {
                    "name": ore["name"],
                    "count": count,
                    "exp_per_ore": ore["exp"],
                    "exp_total": count * ore["exp"],
                    "item_id": ore["item_id"],
                    "icon_url": resolve_icon_url(item_id=ore["item_id"], name=ore["name"]),
                }
            )
            ore_count += count
            remaining -= count * ore["exp"]
    return {
        "total_exp": total_exp,
        "ores": ores_out,
        "ore_count": ore_count,
        "remainder_exp": remaining,
    }


def weapon_exp_block(level_exp: list[int], from_level: int, to_level: int) -> dict:
    total = exp_for_level_range(level_exp, from_level, to_level)
    plan = ores_for_exp(total)
    return {
        "from_level": from_level,
        "to_level": to_level,
        "mora_cost": total // 10,
        "mora_per_exp": "1 mora per 10 EXP",
        **plan,
    }
