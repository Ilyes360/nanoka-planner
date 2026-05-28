"""Tests pour talent_report.py."""

from __future__ import annotations

import json
from pathlib import Path

from nanoka import talent_report


def test_build_talent_report_tracks_and_totals() -> None:
    char = {
        "name": "Tester",
        "id": "10000099",
        "url": "https://gi.nanoka.cc/character/10000099",
        "talents": [
            {
                "track": 1,
                "levels": [
                    {"level": 2, "cost": 100, "materials": [{"name": "Slime", "count": 2, "item": {}}]},
                    {"level": 3, "cost": 200, "materials": [{"name": "Book", "count": 1, "item": {}}]},
                ],
            }
        ],
    }
    report = talent_report.build_talent_report(char)
    assert report["level_count"] == 2
    assert report["total_mora"] == 300
    assert report["level_range"] == {"min": 1, "max": 10}
    assert {row["name"] for row in report["totals"]} == {"Book", "Slime"}
    track = report["talents"][0]
    assert track["track"] == 1
    assert track["level_count"] == 2
    assert track["total_mora"] == 300
    assert [lvl["level"] for lvl in track["levels"]] == [3, 4]


def test_build_all_talent_reports_sorted(sample_character_raw: dict, item_lookup) -> None:
    from nanoka import assign

    by_id, by_name = item_lookup
    c1 = assign.character_loadout(sample_character_raw, by_id, by_name)
    c2 = dict(c1)
    c2["name"] = "Alice"
    reports = talent_report.build_all_talent_reports([c1, c2])
    assert [r["name"] for r in reports] == ["Alice", "Tester"]


def test_talent_levels_outside_1_to_10_are_ignored() -> None:
    char = {
        "name": "Tester",
        "id": "10000099",
        "talents": [
            {
                "track": 1,
                "levels": [
                    {"level": 0, "cost": 10, "materials": [{"name": "X", "count": 1}]},
                    {"level": 1, "cost": 100, "materials": [{"name": "Slime", "count": 2}]},
                    {"level": 2, "cost": 120, "materials": [{"name": "Book", "count": 1}]},
                    {"level": 9, "cost": 700000, "materials": [{"name": "Crown", "count": 1}]},
                    {"level": 10, "cost": 800000, "materials": [{"name": "Y", "count": 1}]},
                ],
            }
        ],
    }
    report = talent_report.build_talent_report(char)
    levels = [lvl["level"] for lvl in report["talents"][0]["levels"]]
    assert levels == [2, 3, 10]


def test_talent_report_main_filter(tmp_path: Path, sample_character_raw: dict, item_lookup, monkeypatch, capsys) -> None:
    from nanoka import assign

    by_id, by_name = item_lookup
    loadouts = [
        assign.character_loadout(sample_character_raw, by_id, by_name),
        {**assign.character_loadout(sample_character_raw, by_id, by_name), "name": "Other"},
    ]
    loadouts_path = tmp_path / "char_loadouts.json"
    out = tmp_path / "talent_report.json"
    loadouts_path.write_text(json.dumps(loadouts), encoding="utf-8")
    monkeypatch.setattr(
        talent_report,
        "parse_args",
        lambda: talent_report.argparse.Namespace(loadouts=loadouts_path, out=out, character="test", show=False),
    )
    talent_report.main()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert len(data) == 1
    assert data[0]["name"] == "Tester"
    assert "Rapport talents personnages" in capsys.readouterr().out


def test_aggregate_talent_track_level_one_is_empty() -> None:
    track = {
        "track": 1,
        "levels": [
            {"level": 2, "mora": 100, "materials": [{"name": "Slime", "count": 2}]},
            {"level": 3, "mora": 200, "materials": [{"name": "Book", "count": 1}]},
        ],
    }
    row = talent_report.aggregate_talent_track(track, 1)
    assert row["materials"] == []
    assert row["total_mora"] == 0
    assert row["target_level"] == 1


def test_aggregate_talent_track_up_to_target_level() -> None:
    track = {
        "track": 2,
        "levels": [
            {"level": 2, "mora": 100, "materials": [{"name": "Slime", "count": 2}]},
            {"level": 3, "mora": 200, "materials": [{"name": "Book", "count": 1}]},
            {"level": 4, "mora": 300, "materials": [{"name": "Book", "count": 2}]},
        ],
    }
    row = talent_report.aggregate_talent_track(track, 3)
    assert row["total_mora"] == 300
    assert {m["name"] for m in row["materials"]} == {"Book", "Slime"}
    assert sum(m["count"] for m in row["materials"] if m["name"] == "Book") == 1


def test_aggregate_talent_report_with_levels_per_track() -> None:
    report = {
        "talents": [
            {
                "track": 1,
                "levels": [{"level": 2, "mora": 10, "materials": [{"name": "A", "count": 1}]}],
            },
            {
                "track": 2,
                "levels": [{"level": 2, "mora": 20, "materials": [{"name": "B", "count": 2}]}],
            },
            {
                "track": 3,
                "levels": [{"level": 2, "mora": 30, "materials": [{"name": "C", "count": 3}]}],
            },
        ],
    }
    plan = talent_report.aggregate_talent_report_with_levels(report, {1: 2, 2: 1, 3: 1})
    assert plan["total"]["total_mora"] == 10
    assert {m["name"] for m in plan["total"]["materials"]} == {"A"}
    assert plan["tracks"][1]["total_mora"] == 0
    assert plan["tracks"][2]["total_mora"] == 0


def test_parse_talent_levels_param_comma_and_equals() -> None:
    report = {"talents": [{"track": 1}, {"track": 2}, {"track": 3}]}
    assert talent_report.parse_talent_levels_param("10,6,1", report) == {1: 10, 2: 6, 3: 1}
    assert talent_report.parse_talent_levels_param("1=10,3=1", report) == {1: 10, 3: 1}


def test_talent_levels_constant_matches_frontend() -> None:
    assert talent_report.TALENT_LEVELS == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


def test_print_talent_report_outputs_levels_and_totals(capsys) -> None:
    report = {
        "name": "Tester",
        "id": "10000099",
        "talents": [
            {
                "track": 1,
                "levels": [{"level": 2, "mora": 100, "materials": [{"name": "Slime", "count": 2}]}],
                "totals": [{"name": "Slime", "count": 2}],
                "total_mora": 100,
            }
        ],
        "totals": [{"name": "Slime", "count": 2}],
        "total_mora": 100,
    }
    talent_report.print_talent_report(report)
    out = capsys.readouterr().out
    assert "Niveau 2" in out
    assert "Slime" in out
    assert "Cumul materiaux" in out
