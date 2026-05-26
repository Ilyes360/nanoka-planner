"""Tests pour migrate_paths.py."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from nanoka import paths
from nanoka import migrate_paths


class TestNormalizeLocalPath:
    def test_legacy_character_folder(self, project_root: Path) -> None:
        raw = "downloaded_character_images\\10000121_aino\\001.webp"
        fixed = migrate_paths.normalize_local_path(raw)
        assert fixed == "data/images/characters/10000121_aino/001.webp"

    def test_legacy_weapon_forward_slash(self) -> None:
        raw = "downloaded_weapon_images/11401_sword/icon.webp"
        fixed = migrate_paths.normalize_local_path(raw)
        assert fixed.startswith("data/images/weapons/")
        assert "\\" not in fixed

    def test_legacy_item_folder(self) -> None:
        raw = "downloaded_item_images/333101_card/icon.webp"
        assert "data/images/items/" in migrate_paths.normalize_local_path(raw)

    def test_fix_corrupted_backslash_after_migration(self) -> None:
        raw = "data/images/characters\\10000121_aino\\001.webp"
        fixed = migrate_paths.normalize_local_path(raw)
        assert fixed == "data/images/characters/10000121_aino/001.webp"

    def test_collapses_double_slashes(self) -> None:
        raw = "data/images/characters//10000121_aino//001.webp"
        assert "//" not in migrate_paths.normalize_local_path(raw)

    def test_already_normalized_unchanged(self) -> None:
        raw = "data/images/characters/10000121_aino/001.webp"
        assert migrate_paths.normalize_local_path(raw) == raw


class TestRewriteFile:
    def test_missing_file(self, tmp_path: Path) -> None:
        assert migrate_paths.rewrite_file(tmp_path / "missing.json") == 0

    def test_dry_run_no_write(self, tmp_path: Path) -> None:
        path = tmp_path / "data.json"
        path.write_text(
            '{"images":[{"local_path": "downloaded_character_images\\\\100\\\\a.webp"}]}',
            encoding="utf-8",
        )
        assert migrate_paths.rewrite_file(path, dry_run=True) == 1
        assert "downloaded_character_images" in path.read_text(encoding="utf-8")

    def test_rewrite_produces_valid_json(self, tmp_path: Path) -> None:
        path = tmp_path / "chars.json"
        path.write_text(
            json.dumps(
                {
                    "character_images": [
                        {"url": "http://x", "local_path": "downloaded_character_images\\1_a\\f.webp"}
                    ]
                }
            ),
            encoding="utf-8",
        )
        assert migrate_paths.rewrite_file(path) == 1
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["character_images"][0]["local_path"].startswith("data/images/characters/")
        assert "\\" not in data["character_images"][0]["local_path"]

    def test_no_change_returns_zero(self, tmp_path: Path) -> None:
        path = tmp_path / "ok.json"
        content = '{"local_path": "data/images/characters/1/a.webp"}'
        path.write_text(content, encoding="utf-8")
        assert migrate_paths.rewrite_file(path) == 0

    def test_unicode_in_path(self, tmp_path: Path) -> None:
        path = tmp_path / "u.json"
        path.write_text(
            json.dumps({"local_path": "downloaded_item_images/1_café/file.webp"}),
            encoding="utf-8",
        )
        migrate_paths.rewrite_file(path)
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "data/images/items/" in data["local_path"]


class TestMigrateMain:
    def test_main_dry_run(self, tmp_path: Path, monkeypatch, capsys) -> None:
        monkeypatch.setattr(migrate_paths, "RAW", tmp_path)
        (tmp_path / "a.json").write_text(
            '{"local_path": "downloaded_weapon_images/x/y.webp"}', encoding="utf-8"
        )
        monkeypatch.setattr(
            migrate_paths,
            "parse_args",
            lambda: argparse.Namespace(dry_run=True),
        )
        migrate_paths.main()
        out = capsys.readouterr().out
        assert "OK: a.json" in out
        assert "downloaded_weapon_images" in (tmp_path / "a.json").read_text(encoding="utf-8")
