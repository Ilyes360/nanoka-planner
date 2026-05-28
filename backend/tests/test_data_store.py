"""Tests pour data_store.py."""

from __future__ import annotations

import json
from pathlib import Path

from nanoka import data_store


def test_loadout_lookup_uses_cache(tmp_path: Path) -> None:
    path = tmp_path / "character_loadouts.json"
    row = {"id": "10000001", "name": "A", "url": "https://gi.nanoka.cc/character/10000001"}
    path.write_text(json.dumps([row]), encoding="utf-8")

    data_store.clear_caches()
    data_store._cached_list(path)
    path.write_text(json.dumps([{**row, "name": "B"}]), encoding="utf-8")

    cached = data_store._cached_list(path)
    assert cached[0]["name"] == "A"

    data_store.clear_caches()
    refreshed = data_store._cached_list(path)
    assert refreshed[0]["name"] == "B"
