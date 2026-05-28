"""Tests pour weapon_report.py."""

from __future__ import annotations

import json
from pathlib import Path

from nanoka import weapon_report


def test_build_weapon_report_totals_and_mora() -> None:
    weapon = {
        "name": "Test Sword",
        "id": "11401",
        "url": "https://gi.nanoka.cc/weapon/11401",
        "ascensions": [
            {"phase": 1, "cost": 500, "materials": [{"name": "Mora", "count": 1, "item": {}}]},
            {"phase": 2, "cost": 1500, "materials": [{"name": "Ore", "count": 4, "item": {}}]},
        ],
    }
    report = weapon_report.build_weapon_report(weapon)
    assert report["total_mora"] == 2000
    assert len(report["ascensions"]) == 2
    assert {row["name"] for row in report["totals"]} == {"Mora", "Ore"}
    mats = report["enhancement_exp"]["materials"]
    assert any(m["name"] == "Mystic Enhancement Ore" and m["exp"] == 10_000 for m in mats)
    assert "exp_books_total" not in report


def test_build_all_weapon_reports_sorted(sample_weapon_raw: dict, item_lookup) -> None:
    from nanoka import assign

    by_id, by_name = item_lookup
    w1 = assign.weapon_loadout(sample_weapon_raw, by_id, by_name)
    w2 = dict(w1)
    w2["name"] = "A Sword"
    reports = weapon_report.build_all_weapon_reports([w1, w2])
    assert [r["name"] for r in reports] == ["A Sword", "Test Sword"]


def test_weapon_report_main_filter(tmp_path: Path, sample_weapon_raw: dict, item_lookup, monkeypatch, capsys) -> None:
    from nanoka import assign

    by_id, by_name = item_lookup
    loadouts = [
        assign.weapon_loadout(sample_weapon_raw, by_id, by_name),
        {**assign.weapon_loadout(sample_weapon_raw, by_id, by_name), "name": "Other"},
    ]
    loadouts_path = tmp_path / "weapon_loadouts.json"
    out = tmp_path / "weapon_report.json"
    loadouts_path.write_text(json.dumps(loadouts), encoding="utf-8")
    monkeypatch.setattr(
        weapon_report,
        "parse_args",
        lambda: weapon_report.argparse.Namespace(loadouts=loadouts_path, out=out, weapon="test", show=False),
    )
    weapon_report.main()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert len(data) == 1
    assert data[0]["name"] == "Test Sword"
    assert "Rapport ascension armes" in capsys.readouterr().out


def test_print_weapon_report_outputs_materials(capsys) -> None:
    report = {
        "name": "Test Sword",
        "id": "11401",
        "ascensions": [
            {"label": "Ascension 1", "mora": 500, "materials": [{"name": "Mora", "count": 1}]},
        ],
        "totals": [{"name": "Mora", "count": 1}],
        "total_mora": 500,
        "enhancement_exp": {"materials": [{"name": "Mystic Enhancement Ore", "exp": 10000}], "mora_per_exp": "1"},
    }
    weapon_report.print_weapon_report(report)
    out = capsys.readouterr().out
    assert "Ascension 1" in out
    assert "Mora" in out
    assert "Mystic Enhancement Ore" in out
