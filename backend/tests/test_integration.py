"""Tests d'intégration légers entre modules."""

from __future__ import annotations

import json
from pathlib import Path

from nanoka import ascension_report, assign, talent_report, weapon_report


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
    weapon_loadout = assign.weapon_loadout(sample_weapon_raw, by_id, by_name)
    w_report = weapon_report.build_weapon_report(weapon_loadout)
    assert w_report["name"] == "Test Sword"
    assert w_report["ascensions"]
    assert w_report["ascensions"][0].get("leveling")
    assert w_report["enhancement_ores_total"]

    t_report = talent_report.build_talent_report(loadout)
    assert t_report["name"] == "Tester"
    assert t_report["talents"]


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


def test_build_all_weapon_and_talent_reports(
    sample_character_raw: dict,
    sample_weapon_raw: dict,
    items_catalog: list[dict],
) -> None:
    by_id, by_name = assign.build_item_lookup(items_catalog)
    char_loadout = assign.character_loadout(sample_character_raw, by_id, by_name)
    weapon_loadout = assign.weapon_loadout(sample_weapon_raw, by_id, by_name)

    weapon_reports = weapon_report.build_all_weapon_reports([weapon_loadout])
    talent_reports = talent_report.build_all_talent_reports([char_loadout])
    assert weapon_reports[0]["name"] == "Test Sword"
    assert talent_reports[0]["name"] == "Tester"
