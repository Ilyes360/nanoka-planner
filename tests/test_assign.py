"""Tests pour assign.py."""

from __future__ import annotations

import json
from pathlib import Path

from nanoka import assign
import pytest


class TestEntityId:
    @pytest.mark.parametrize(
        "url,kind,expected",
        [
            ("https://gi.nanoka.cc/character/10000021", "character", "10000021"),
            ("https://gi.nanoka.cc/character/10000021/", "character", "10000021"),
            ("https://gi.nanoka.cc/weapon/11401", "weapon", "11401"),
            ("", "character", ""),
            ("https://example.com/nope", "character", ""),
        ],
    )
    def test_entity_id(self, url: str, kind: str, expected: str) -> None:
        assert assign.entity_id(url, kind) == expected


class TestItemIdFromUrl:
    def test_valid(self) -> None:
        assert assign.item_id_from_url("https://gi.nanoka.cc/item/104121") == 104121

    def test_invalid(self) -> None:
        assert assign.item_id_from_url("https://gi.nanoka.cc/character/1") is None


class TestBuildItemLookup:
    def test_by_id_and_name(self, items_catalog: list[dict]) -> None:
        by_id, by_name = assign.build_item_lookup(items_catalog)
        assert by_id[202]["name"] == "Mora"
        assert by_name["slime condensate"]["name"] == "Slime Condensate"

    def test_duplicate_names_keep_first(self) -> None:
        items = [
            {"name": "Dup", "url": "https://gi.nanoka.cc/item/1"},
            {"name": "Dup", "url": "https://gi.nanoka.cc/item/2"},
        ]
        _, by_name = assign.build_item_lookup(items)
        assert assign.item_id_from_url(by_name["dup"]["url"]) == 1

    def test_empty_catalog(self) -> None:
        by_id, by_name = assign.build_item_lookup([])
        assert by_id == {}
        assert by_name == {}


class TestItemSummary:
    def test_unmatched(self) -> None:
        summary = assign.item_summary(None, mat_id=999)
        assert summary["matched"] is False
        assert summary["item_id"] == 999

    def test_matched_with_image(self, sample_item: dict) -> None:
        summary = assign.item_summary(sample_item)
        assert summary["matched"] is True
        assert summary["item_id"] == 202
        assert "UI_ItemIcon_202" in summary["icon_url"]

    def test_icon_from_raw_when_no_images(self, sample_item_by_name: dict) -> None:
        summary = assign.item_summary(sample_item_by_name)
        assert summary["icon_url"].endswith("UI_ItemIcon_112002.webp")


class TestResolveItem:
    def test_by_int_id(self, item_lookup) -> None:
        by_id, by_name = item_lookup
        row = assign.resolve_item({"name": "X", "id": 202}, by_id, by_name)
        assert row is not None
        assert row["name"] == "Mora"

    def test_by_string_id(self, item_lookup) -> None:
        by_id, by_name = item_lookup
        row = assign.resolve_item({"name": "X", "id": "112002"}, by_id, by_name)
        assert row["name"] == "Slime Condensate"

    def test_by_name_fallback(self, item_lookup) -> None:
        by_id, by_name = item_lookup
        row = assign.resolve_item({"name": "Slime Condensate", "id": 0}, by_id, by_name)
        assert row is not None

    def test_unknown(self, item_lookup) -> None:
        by_id, by_name = item_lookup
        assert assign.resolve_item({"name": "Missing", "id": 1}, by_id, by_name) is None


class TestEnrichMat:
    def test_enrich_known(self, item_lookup) -> None:
        by_id, by_name = item_lookup
        out = assign.enrich_mat({"name": "Mora", "id": 202, "count": 5}, by_id, by_name)
        assert out["item"]["matched"] is True
        assert out["count"] == 5


class TestEnrichStep:
    def test_renames_mats_to_materials(self, item_lookup) -> None:
        by_id, by_name = item_lookup
        step = {"cost": 100, "mats": [{"name": "Mora", "id": 202, "count": 1}]}
        out = assign.enrich_step(step, by_id, by_name)
        assert "mats" not in out
        assert out["cost"] == 100
        assert len(out["materials"]) == 1


class TestCharacterLoadout:
    def test_ascensions_and_talents(self, sample_character_raw: dict, item_lookup) -> None:
        by_id, by_name = item_lookup
        sample_character_raw["raw_data"]["level_exp"] = [100, 200, 300]
        out = assign.character_loadout(sample_character_raw, by_id, by_name)
        assert out["id"] == "10000099"
        assert out["level_exp"] == [100, 200, 300]
        assert len(out["ascensions"]) == 2
        assert out["ascensions"][0]["phase"] == 1
        assert len(out["ascensions"][0]["materials"]) == 2
        assert len(out["talents"]) == 1
        assert len(out["talents"][0]["levels"]) == 1

    def test_missing_materials(self, item_lookup) -> None:
        by_id, by_name = item_lookup
        char = {"name": "Empty", "url": "https://gi.nanoka.cc/character/1", "raw_data": {}}
        out = assign.character_loadout(char, by_id, by_name)
        assert out["ascensions"] == []
        assert out["talents"] == []


class TestWeaponLoadout:
    def test_phases_sorted(self, sample_weapon_raw: dict, item_lookup) -> None:
        by_id, by_name = item_lookup
        out = assign.weapon_loadout(sample_weapon_raw, by_id, by_name)
        assert out["id"] == "11401"
        assert [p["phase"] for p in out["ascensions"]] == [1, 2]
        assert out["ascensions"][1]["materials"][0]["item"]["matched"] is False


class TestIterMatsFromEntity:
    def test_character_includes_talents(self, sample_character_raw: dict) -> None:
        mats = assign.iter_mats_from_entity(sample_character_raw, "ascension")
        names = [m["name"] for m in mats]
        assert names.count("Mora") == 2
        assert "Slime Condensate" in names

    def test_weapon_materials(self, sample_weapon_raw: dict) -> None:
        mats = assign.iter_mats_from_entity(sample_weapon_raw, "weapon_ascension")
        assert len(mats) == 2

    def test_skips_blank_names(self) -> None:
        entity = {
            "raw_data": {
                "materials": {
                    "ascensions": [{"mats": [{"name": "  ", "count": 1}, {"name": "OK", "count": 1}]}]
                }
            }
        }
        assert len(assign.iter_mats_from_entity(entity, "ascension")) == 1


class TestBuildUsageIndex:
    def test_used_by_and_quantities(
        self, sample_character_raw: dict, sample_weapon_raw: dict, item_lookup
    ) -> None:
        by_id, by_name = item_lookup
        entities = [sample_character_raw, sample_weapon_raw]
        index = assign.build_usage_index(entities, "character", by_id, by_name)
        mora = next(r for r in index if r["name"] == "Mora")
        assert "1" in mora["seen_quantities"]
        assert "2" in mora["seen_quantities"]
        assert len(mora["used_by"]) == 1
        assert mora["used_by"][0]["name"] == "Tester"

    def test_weapon_index(self, sample_weapon_raw: dict, item_lookup) -> None:
        by_id, by_name = item_lookup
        index = assign.build_usage_index([sample_weapon_raw], "weapon", by_id, by_name)
        unknown = next(r for r in index if r["name"] == "Unknown Ore")
        assert unknown["item"]["matched"] is False

    def test_no_duplicate_used_by(self, sample_character_raw: dict, item_lookup) -> None:
        by_id, by_name = item_lookup
        dup = dict(sample_character_raw)
        dup["name"] = "Tester Clone"
        index = assign.build_usage_index([sample_character_raw, dup], "character", by_id, by_name)
        mora = next(r for r in index if r["name"] == "Mora")
        assert len(mora["used_by"]) == 2

    def test_sorted_by_name(self, item_lookup) -> None:
        by_id, by_name = item_lookup
        e1 = {
            "name": "Z",
            "url": "https://gi.nanoka.cc/character/1",
            "raw_data": {"materials": {"ascensions": [{"mats": [{"name": "ZZZ", "count": 1}]}]}},
        }
        e2 = {
            "name": "A",
            "url": "https://gi.nanoka.cc/character/2",
            "raw_data": {"materials": {"ascensions": [{"mats": [{"name": "AAA", "count": 1}]}]}},
        }
        index = assign.build_usage_index([e1, e2], "character", by_id, by_name)
        assert [r["name"] for r in index] == ["AAA", "ZZZ"]


class TestAssignMain:
    def test_main_writes_outputs(
        self,
        tmp_path: Path,
        sample_character_raw: dict,
        sample_weapon_raw: dict,
        items_catalog: list[dict],
        monkeypatch,
        capsys,
    ) -> None:
        chars = tmp_path / "chars.json"
        weapons = tmp_path / "weapons.json"
        items = tmp_path / "items.json"
        chars.write_text(json.dumps([sample_character_raw]), encoding="utf-8")
        weapons.write_text(json.dumps([sample_weapon_raw]), encoding="utf-8")
        items.write_text(json.dumps(items_catalog), encoding="utf-8")

        out_char = tmp_path / "out" / "char_loadouts.json"
        out_weapon = tmp_path / "out" / "weapon_loadouts.json"
        out_ci = tmp_path / "out" / "char_items.json"
        out_wi = tmp_path / "out" / "weapon_items.json"

        monkeypatch.setattr(
            assign,
            "parse_args",
            lambda: assign.argparse.Namespace(
                characters=chars,
                weapons=weapons,
                items=items,
                character_loadouts_out=out_char,
                weapon_loadouts_out=out_weapon,
                character_items_out=out_ci,
                weapon_items_out=out_wi,
            ),
        )

        assign.main()

        assert out_char.is_file()
        assert out_weapon.is_file()
        loadouts = json.loads(out_char.read_text(encoding="utf-8"))
        assert loadouts[0]["name"] == "Tester"
        assert "Characters:" in capsys.readouterr().out
