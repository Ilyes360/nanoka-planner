"""Libellés affichables (élément, type d'arme, rareté, région)."""

from __future__ import annotations

from typing import Any

REGION_LABELS: dict[str, str] = {
    "ASSOC_TYPE_MONDSTADT": "Mondstadt",
    "ASSOC_TYPE_LIYUE": "Liyue",
    "ASSOC_TYPE_INAZUMA": "Inazuma",
    "ASSOC_TYPE_SUMERU": "Sumeru",
    "ASSOC_TYPE_FONTAINE": "Fontaine",
    "ASSOC_TYPE_NATLAN": "Natlan",
    "ASSOC_TYPE_NODKRAI": "Nod-Krai",
}

WEAPON_LABELS: dict[str, str] = {
    "WEAPON_SWORD": "Sword",
    "WEAPON_SWORD_ONE_HAND": "Sword",
    "WEAPON_CLAYMORE": "Claymore",
    "WEAPON_POLE": "Polearm",
    "WEAPON_BOW": "Bow",
    "WEAPON_CATALYST": "Catalyst",
}


def weapon_type_label(key: str) -> str:
    key = str(key or "").strip()
    if not key:
        return ""
    if key in WEAPON_LABELS:
        return WEAPON_LABELS[key]
    return key.replace("WEAPON_", "").replace("_", " ").strip().title()


def rarity_label(value: Any) -> str:
    try:
        stars = int(value)
    except (TypeError, ValueError):
        return str(value or "").strip()
    if 1 <= stars <= 5:
        return f"{stars}★"
    return str(value).strip()


CHARACTER_RARITY_LABELS: dict[str, str] = {
    "QUALITY_ORANGE": "5★",
    "QUALITY_ORANGE_SP": "5★",
    "QUALITY_PURPLE": "4★",
}


def character_rarity_label(value: Any) -> str:
    key = str(value or "").strip()
    if not key:
        return ""
    if key in CHARACTER_RARITY_LABELS:
        return CHARACTER_RARITY_LABELS[key]
    return rarity_label(value)
