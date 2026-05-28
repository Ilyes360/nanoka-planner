"""Tests pour scrape.py (fonctions pures et parsing)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from nanoka import scrape
from nanoka.scrape import AscensionItem, ScrapedEntry


class TestSlugify:
    @pytest.mark.parametrize(
        "text,expected",
        [
            ("Aino", "aino"),
            ("  Hello World! ", "hello_world"),
            ("___", "unknown"),
            ("", "unknown"),
            ("Jean-Luc", "jean_luc"),
        ],
    )
    def test_slugify(self, text: str, expected: str) -> None:
        assert scrape.slugify(text) == expected


class TestIconToUrl:
    def test_absolute_url_unchanged(self) -> None:
        url = "https://cdn.example.com/icon.webp"
        assert scrape.icon_to_url(url) == url

    def test_adds_webp_extension(self) -> None:
        assert scrape.icon_to_url("UI_ItemIcon_202").endswith("UI_ItemIcon_202.webp")

    def test_keeps_existing_extension(self) -> None:
        icon = "subdir/UI_ItemIcon_202.png"
        assert scrape.icon_to_url(icon).endswith("subdir/UI_ItemIcon_202.png")


class TestImageFilename:
    def test_deterministic_hash(self) -> None:
        url = "https://static.nanoka.cc/assets/gi/test.webp"
        assert scrape.image_filename(url) == scrape.image_filename(url)
        assert scrape.image_filename(url).endswith(".webp")

    def test_default_extension_when_missing(self) -> None:
        name = scrape.image_filename("https://example.com/noext")
        assert name.endswith(".img")


class TestCollectIconNames:
    def test_nested_dict_and_list(self) -> None:
        payload = {
            "icon": " UI_Main ",
            "child": [{"icon": "UI_Child"}, {"x": 1}],
            "other": "UI_Ignored",
        }
        out: set[str] = set()
        scrape.collect_icon_names(payload, out)
        assert out == {"UI_Main", "UI_Child"}


class TestExpandCharacterIcons:
    def test_base_avatar_icon(self) -> None:
        data = {"icon": "UI_AvatarIcon_Aino"}
        icons = scrape.expand_character_icons(data)
        assert "UI_Gacha_AvatarImg_Aino" in icons
        assert "UI_AvatarIcon_Side_Aino" in icons

    def test_costume_icons(self) -> None:
        data = {
            "icon": "UI_Other",
            "chara_info": {"costume": [{"icon": "UI_AvatarIcon_Costume"}]},
        }
        icons = scrape.expand_character_icons(data)
        assert "UI_Costume_Costume" in icons
        assert "UI_AvatarIcon_Costume" in icons

    def test_no_avatar_prefix(self) -> None:
        assert scrape.expand_character_icons({"icon": "UI_ItemIcon_1"}) == set()


class TestDedupe:
    def test_removes_duplicates(self) -> None:
        items = [
            AscensionItem("Gem", "1", "Gem 1"),
            AscensionItem("Gem", "1", "Gem 1"),
            AscensionItem("gem", "1", "gem 1"),
        ]
        assert len(scrape.dedupe(items)) == 1


class TestExtractIdsFromListing:
    def test_extracts_sorted_unique_ids(self) -> None:
        html = '<a href="/character/10000002">a</a><a href="/character/10000003/">b</a>'
        with patch.object(scrape, "get_text", return_value=html):
            assert scrape.extract_ids_from_listing("http://x", "character") == ["10000002", "10000003"]


class TestParseCharacter:
    def test_parses_ascension_and_talents(self, tmp_path: Path) -> None:
        data = {
            "name": "Unit",
            "icon": "UI_AvatarIcon_Unit",
            "weapon": "WEAPON_SWORD",
            "chara_info": {"vision": "Pyro", "title": "Title", "costume": []},
            "materials": {
                "ascensions": [{"mats": [{"name": "Ore", "count": 2}]}],
                "talents": [[{"mats": [{"name": "Book", "count": 3}]}]],
            },
        }
        entry = scrape.parse_character("99", data, tmp_path / "img", dl=False)
        assert entry.name == "Unit"
        assert entry.type == "character"
        assert len(entry.ascension) == 2
        assert "Pyro" in entry.page_facts
        assert entry.url.endswith("/character/99")


class TestParseWeapon:
    def test_parses_weapon_materials(self, tmp_path: Path) -> None:
        data = {
            "name": "Blade",
            "icon": "UI_EquipIcon_Sword",
            "weapon_type": "WEAPON_SWORD_ONE_HAND",
            "rarity": 5,
            "materials": {"2": {"mats": [{"name": "Tile", "count": 4}]}},
        }
        entry = scrape.parse_weapon("11401", data, tmp_path / "img", dl=False)
        assert entry.name == "Blade"
        assert len(entry.weapon_ascension) == 1
        assert "SWORD" in " ".join(entry.page_facts)


class TestParseItems:
    def test_respects_max_items(self, tmp_path: Path) -> None:
        item_all = {
            "1": {"name": "A", "icon": "UI_A"},
            "2": {"name": "B", "icon": "UI_B"},
            "3": {"name": "C", "icon": "UI_C"},
        }
        entries = scrape.parse_items(item_all, tmp_path / "items", dl=False, max_items=2)
        assert len(entries) == 2
        assert all(e.type == "item" for e in entries)

    def test_skips_non_dict_rows(self, tmp_path: Path) -> None:
        entries = scrape.parse_items({"1": "bad", "2": {"name": "OK", "icon": "I"}}, tmp_path, False, 0)
        assert len(entries) == 1


class TestCollectImages:
    def test_without_download(self, tmp_path: Path) -> None:
        rows = scrape.collect_images({"UI_A", "UI_B"}, "1", "Name", tmp_path, with_download=False)
        assert len(rows) == 2
        assert "local_path" not in rows[0]

    def test_deduplicates_urls(self, tmp_path: Path) -> None:
        rows = scrape.collect_images({"UI_Same", "UI_Same"}, "1", "X", tmp_path, False)
        assert len(rows) == 1

    @patch.object(scrape, "download", return_value=True)
    def test_with_download_writes_relative_path(
        self, _mock_dl: MagicMock, tmp_path: Path, monkeypatch
    ) -> None:
        monkeypatch.setattr(scrape, "relative_to_root", lambda p: f"rel/{p.name}")
        rows = scrape.collect_images({"UI_X"}, "42", "Hero", tmp_path, with_download=True)
        assert len(rows) == 1
        assert rows[0]["local_path"].startswith("rel/")
        assert (tmp_path / "42_hero").is_dir()


class TestExportAll:
    def test_splits_entity_types(self, tmp_path: Path) -> None:
        entries = [
            ScrapedEntry("C", "character", "http://c", ascension=[AscensionItem("M", "1", "M 1")]),
            ScrapedEntry("W", "weapon", "http://w", weapon_ascension=[AscensionItem("Wm", "2", "Wm 2")]),
            ScrapedEntry("I", "item", "http://i"),
        ]
        chars = tmp_path / "c.json"
        weapons = tmp_path / "w.json"
        items = tmp_path / "i.json"
        ci = tmp_path / "ci.json"
        wi = tmp_path / "wi.json"
        scrape.export_all(entries, chars, weapons, items, ci, wi)

        assert len(json.loads(chars.read_text(encoding="utf-8"))) == 1
        assert len(json.loads(weapons.read_text(encoding="utf-8"))) == 1
        assert len(json.loads(items.read_text(encoding="utf-8"))) == 1
        char_items = json.loads(ci.read_text(encoding="utf-8"))
        assert char_items[0]["name"] == "M"
        assert char_items[0]["seen_quantities"] == ["1"]
