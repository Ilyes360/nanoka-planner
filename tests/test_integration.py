"""Tests d'intégration légers entre modules."""

from __future__ import annotations

import json
from pathlib import Path

from nanoka import ascension_report, assign


def test_assign_then_ascension_report_pipeline(
    sample_character_raw: dict,
    sample_weapon_raw: dict,
    items_catalog: list[dict],
    tmp_path: Path,
) -> None:
    by_id, by_name = assign.build_item_lookup(items_catalog)
    loadout = assign.character_loadout(sample_character_raw, by_id, by_name)

    report = ascension_report.build_character_report(loadout)
    assert report["name"] == "Tester"
    assert report["total_mora"] > 0
    assert len(report["ascensions"]) == len(loadout["ascensions"])

    for step in report["ascensions"]:
        for mat in step["materials"]:
            if mat["name"] == "Mora":
                assert mat["item_id"] == 202
                assert mat["count"] > 0


def test_full_assign_outputs_loadable_by_report(
    tmp_path: Path,
    sample_character_raw: dict,
    items_catalog: list[dict],
) -> None:
    chars_path = tmp_path / "chars.json"
    chars_path.write_text(json.dumps([sample_character_raw]), encoding="utf-8")
    items_path = tmp_path / "items.json"
    items_path.write_text(json.dumps(items_catalog), encoding="utf-8")

    characters = json.loads(chars_path.read_text(encoding="utf-8"))
    items = json.loads(items_path.read_text(encoding="utf-8"))
    by_id, by_name = assign.build_item_lookup(items)
    loadouts = [assign.character_loadout(c, by_id, by_name) for c in characters]

    out = tmp_path / "report.json"
    reports = ascension_report.build_all_reports(loadouts)
    out.write_text(json.dumps(reports, ensure_ascii=False, indent=2), encoding="utf-8")

    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded[0]["totals"]
