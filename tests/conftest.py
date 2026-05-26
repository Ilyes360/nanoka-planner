"""Fixtures partagées pour les tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture
def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def sample_item() -> dict:
    return {
        "name": "Mora",
        "url": "https://gi.nanoka.cc/item/202",
        "item_images": [{"url": "https://static.nanoka.cc/assets/gi/UI_ItemIcon_202.webp"}],
        "item_sources": ["Everywhere"],
        "raw_data": {"icon": "UI_ItemIcon_202", "item_type": "ITEM_MATERIAL", "rank": 1},
    }


@pytest.fixture
def sample_item_by_name() -> dict:
    return {
        "name": "Slime Condensate",
        "url": "https://gi.nanoka.cc/item/112002",
        "item_images": [],
        "raw_data": {"icon": "UI_ItemIcon_112002", "item_type": "ITEM_MATERIAL"},
    }


@pytest.fixture
def sample_character_raw() -> dict:
    return {
        "name": "Tester",
        "url": "https://gi.nanoka.cc/character/10000099",
        "raw_data": {
            "materials": {
                "ascensions": [
                    {
                        "cost": 1000,
                        "mats": [
                            {"name": "Mora", "id": 202, "count": 1},
                            {"name": "Slime Condensate", "id": "112002", "count": 3},
                        ],
                    },
                    {"cost": 2000, "mats": [{"name": "Mora", "id": 202, "count": 2}]},
                ],
                "talents": [
                    [
                        {"cost": 100, "mats": [{"name": "Slime Condensate", "id": 112002, "count": 6}]},
                    ],
                    "not-a-step",
                ],
            }
        },
    }


@pytest.fixture
def sample_weapon_raw() -> dict:
    return {
        "name": "Test Sword",
        "url": "https://gi.nanoka.cc/weapon/11401",
        "raw_data": {
            "materials": {
                "1": {"cost": 500, "mats": [{"name": "Mora", "id": 202, "count": 1}]},
                "2": {"cost": 1500, "mats": [{"name": "Unknown Ore", "id": 999999, "count": 4}]},
            }
        },
    }


@pytest.fixture
def sample_loadout() -> dict:
    return {
        "name": "Tester",
        "id": "10000099",
        "url": "https://gi.nanoka.cc/character/10000099",
        "ascensions": [
            {
                "phase": 1,
                "cost": 20000,
                "materials": [
                    {
                        "name": "Gem Sliver",
                        "count": 1,
                        "id": 104121,
                        "item": {"item_id": 104121, "icon_url": "https://example.com/gem.webp"},
                    },
                    {"name": "Local Special", "count": 3, "id": 101257, "item": {}},
                ],
            },
            {
                "phase": 2,
                "cost": 40000,
                "materials": [
                    {"name": "Local Special", "count": 10, "id": 101257, "item": {}},
                ],
            },
        ],
    }


@pytest.fixture
def items_catalog(sample_item: dict, sample_item_by_name: dict) -> list[dict]:
    return [sample_item, sample_item_by_name]


@pytest.fixture
def item_lookup(items_catalog: list[dict]):
    from nanoka import assign

    return assign.build_item_lookup(items_catalog)
