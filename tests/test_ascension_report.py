"""Tests pour ascension_report.py."""

from __future__ import annotations

import json
from pathlib import Path

import ascension_report
import pytest


class TestPhaseMeta:
    @pytest.mark.parametrize("phase,at_level,cap", [(1, 20, 40), (6, 80, 90)])
    def test_known_phases(self, phase: int, at_level: int, cap: int) -> None:
        meta = ascension_report.phase_meta(phase)
        assert meta["at_level"] == at_level
        assert meta["new_level_cap"] == cap

    def test_unknown_phase(self) -> None:
        meta = ascension_report.phase_meta(99)
        assert meta["at_level"] == 0
        assert meta["new_level_cap"] == 0


class TestSlimMaterial:
    def test_full(self) -> None:
        mat = {
            "name": "Gem",
            "count": "5",
            "id": 1,
            "item": {"item_id": 104121, "icon_url": "https://x/icon.webp"},
        }
        slim = ascension_report.slim_material(mat)
        assert slim == {"name": "Gem", "count": 5, "item_id": 104121, "icon_url": "https://x/icon.webp"}

    def test_missing_item_and_count(self) -> None:
        slim = ascension_report.slim_material({"name": "X"})
        assert slim["count"] == 0
        assert slim["item_id"] is None
        assert slim["icon_url"] == ""


class TestBuildCharacterReport:
    def test_totals_and_mora(self, sample_loadout: dict) -> None:
        report = ascension_report.build_character_report(sample_loadout)
        assert report["total_mora"] == 60000
        assert len(report["ascensions"]) == 2
        assert report["ascensions"][0]["material_count"] == 2
        assert report["ascensions"][0]["label"].startswith("Ascension 1")

        local = next(t for t in report["totals"] if t["name"] == "Local Special")
        assert local["count"] == 13

    def test_exp_books_per_phase(self, sample_loadout: dict) -> None:
        level_exp = [1000] * 89
        index = {"10000099": level_exp}
        report = ascension_report.build_character_report(sample_loadout, index)
        phase1 = report["ascensions"][0]
        assert "leveling" in phase1
        assert phase1["leveling"]["from_level"] == 1
        assert phase1["leveling"]["to_level"] == 20
        assert phase1["leveling"]["book_count"] > 0
        assert report["exp_to_level_90"]["total_exp"] == 89_000
        assert report["exp_books_total"]

    def test_skips_invalid_steps(self) -> None:
        char = {
            "name": "Bad",
            "id": "1",
            "url": "",
            "ascensions": ["not-a-dict", {"phase": 1, "cost": 0, "materials": []}],
        }
        report = ascension_report.build_character_report(char)
        assert len(report["ascensions"]) == 1

    def test_unknown_phase_label(self) -> None:
        char = {
            "name": "X",
            "id": "1",
            "url": "",
            "ascensions": [{"phase": 99, "cost": 0, "materials": []}],
        }
        report = ascension_report.build_character_report(char)
        assert "niv. 0 -> 0" in report["ascensions"][0]["label"]


class TestBuildAllReports:
    def test_sorting_and_filter(self, sample_loadout: dict) -> None:
        z = dict(sample_loadout)
        z["name"] = "Zelda"
        a = dict(sample_loadout)
        a["name"] = "Alice"
        reports = ascension_report.build_all_reports([z, "skip", a])
        assert [r["name"] for r in reports] == ["Alice", "Zelda"]


class TestPrintCharacterReport:
    def test_print_output(self, sample_loadout: dict, capsys) -> None:
        report = ascension_report.build_character_report(
            sample_loadout, {"10000099": [1000] * 89}
        )
        ascension_report.print_character_report(report)
        out = capsys.readouterr().out
        assert "Tester" in out
        assert "Gem Sliver" in out
        assert "Hero's Wit" in out or "livres" in out
        assert "Cumul" in out


class TestAscensionReportMain:
    def test_filter_and_write(
        self, tmp_path: Path, sample_loadout: dict, monkeypatch, capsys
    ) -> None:
        loadouts = tmp_path / "loadouts.json"
        out = tmp_path / "report.json"
        loadouts.write_text(
            json.dumps([sample_loadout, {**sample_loadout, "name": "Other"}]),
            encoding="utf-8",
        )

        monkeypatch.setattr(
            ascension_report,
            "parse_args",
            lambda: ascension_report.argparse.Namespace(
                loadouts=loadouts,
                characters=tmp_path / "missing_chars.json",
                out=out,
                character="test",
                show=False,
            ),
        )
        ascension_report.main()

        data = json.loads(out.read_text(encoding="utf-8"))
        assert len(data) == 1
        assert data[0]["name"] == "Tester"
        assert "1 personnage" in capsys.readouterr().out

    def test_print_no_match(self, tmp_path: Path, monkeypatch, capsys) -> None:
        loadouts = tmp_path / "loadouts.json"
        loadouts.write_text("[]", encoding="utf-8")
        monkeypatch.setattr(
            ascension_report,
            "parse_args",
            lambda: ascension_report.argparse.Namespace(
                loadouts=loadouts,
                characters=tmp_path / "missing_chars.json",
                out=tmp_path / "out.json",
                character="nope",
                show=True,
            ),
        )
        ascension_report.main()
        assert "Aucun personnage" in capsys.readouterr().out
