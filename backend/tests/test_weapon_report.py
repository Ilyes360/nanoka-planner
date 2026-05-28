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
    assert report["enhancement_ores_total"] == []
    assert "enhancement_exp" in report


def test_leveling_80_to_90_after_last_ascension() -> None:
    level_exp = [1000] * 89
    ascensions = [{"phase": p, "cost": 0, "materials": []} for p in range(1, 7)]
    report = weapon_report.build_weapon_report(
        {"name": "Sword", "id": "1", "url": "", "level_exp": level_exp, "ascensions": ascensions}
    )
    after = report["leveling_after_last_ascension"]
    assert after is not None
    assert after["from_level"] == 80
    assert after["to_level"] == 90
    assert after["total_exp"] == 10_000
    assert report["exp_to_level_90"]["total_exp"] == 89_000
    assert sum(r["count"] for r in report["enhancement_ores_total"]) > after["ore_count"]


def test_build_weapon_report_with_level_exp() -> None:
    level_exp = [1000] * 89
    weapon = {
        "name": "Test Sword",
        "id": "11401",
        "url": "https://gi.nanoka.cc/weapon/11401",
        "level_exp": level_exp,
        "ascensions": [
            {"phase": 1, "cost": 500, "materials": []},
            {"phase": 2, "cost": 1500, "materials": []},
        ],
    }
    report = weapon_report.build_weapon_report(weapon)
    phase1 = report["ascensions"][0]
    assert phase1["leveling"]["total_exp"] == 19_000
    assert phase1["leveling"]["mora_cost"] == 1_900
    assert phase1["leveling"]["ore_count"] > 0
    assert report["enhancement_ores_total"]
    assert report["exp_to_level_90"]["total_exp"] == 89_000
    assert "enhancement_exp" not in report


def test_index_weapon_level_exp_from_xp_requirements() -> None:
    weapons = [
        {
            "url": "https://gi.nanoka.cc/weapon/11401",
            "raw_data": {"xp_requirements": {"1": 400, "2": 600}},
        }
    ]
    index = weapon_report.index_weapon_level_exp(weapons)
    assert index["11401"] == [400, 600]


def test_build_all_weapon_reports_sorted(sample_weapon_raw: dict, item_lookup) -> None:
    from nanoka import assign

    by_id, by_name = item_lookup
    w1 = assign.weapon_loadout(sample_weapon_raw, by_id, by_name)
    w2 = dict(w1)
    w2["name"] = "A Sword"
    reports = weapon_report.build_all_weapon_reports([w1, w2])
    assert [r["name"] for r in reports] == ["A Sword", "Test Sword"]
    assert reports[1]["ascensions"][0]["leveling"]["total_exp"] == 19_000


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
        lambda: weapon_report.argparse.Namespace(
            loadouts=loadouts_path,
            weapons=tmp_path / "missing.json",
            out=out,
            weapon="test",
            show=False,
        ),
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
            {
                "label": "Ascension 1 (niv. 20 -> 40)",
                "mora": 500,
                "materials": [{"name": "Mora", "count": 1}],
                "leveling": {
                    "from_level": 1,
                    "to_level": 20,
                    "total_exp": 19_000,
                    "ore_count": 2,
                    "mora_cost": 1_900,
                    "ores": [{"name": "Mystic Enhancement Ore", "count": 1}],
                },
            },
        ],
        "totals": [{"name": "Mora", "count": 1}],
        "total_mora": 500,
        "enhancement_ores_total": [{"name": "Mystic Enhancement Ore", "count": 1}],
        "leveling_mora_total": 1_900,
        "exp_to_level_90": {
            "to_level": 90,
            "total_exp": 89_000,
            "ore_count": 9,
            "mora_cost": 8_900,
            "ores": [],
        },
    }
    weapon_report.print_weapon_report(report)
    out = capsys.readouterr().out
    assert "Ascension 1" in out
    assert "Mora" in out
    assert "minerais" in out
    assert "Mystic Enhancement Ore" in out
