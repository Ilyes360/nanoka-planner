"""Tests pour paths.py."""

from __future__ import annotations

from pathlib import Path

import paths


def test_root_is_project_directory(project_root: Path) -> None:
    assert paths.ROOT == project_root.resolve()


def test_data_paths_under_root(project_root: Path) -> None:
    assert paths.DATA == project_root / "data"
    assert paths.RAW == project_root / "data" / "raw"
    assert paths.PROCESSED == project_root / "data" / "processed"
    assert paths.CHARACTER_IMAGES == project_root / "data" / "images" / "characters"


def test_json_output_paths() -> None:
    assert paths.CHARACTERS_JSON.name == "characters_nanoka.json"
    assert paths.CHARACTER_ASCENSION_REPORT_JSON.parent == paths.PROCESSED


def test_legacy_image_dirs_map_to_new_folders() -> None:
    assert paths.LEGACY_IMAGE_DIRS["downloaded_character_images"] == paths.CHARACTER_IMAGES
    assert paths.LEGACY_IMAGE_DIRS["downloaded_weapon_images"] == paths.WEAPON_IMAGES
    assert paths.LEGACY_IMAGE_DIRS["downloaded_item_images"] == paths.ITEM_IMAGES


def test_ensure_data_dirs_creates_structure(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(paths, "ROOT", tmp_path)
    monkeypatch.setattr(paths, "DATA", tmp_path / "data")
    monkeypatch.setattr(paths, "RAW", tmp_path / "data" / "raw")
    monkeypatch.setattr(paths, "PROCESSED", tmp_path / "data" / "processed")
    monkeypatch.setattr(paths, "CHARACTER_IMAGES", tmp_path / "data" / "images" / "characters")
    monkeypatch.setattr(paths, "WEAPON_IMAGES", tmp_path / "data" / "images" / "weapons")
    monkeypatch.setattr(paths, "ITEM_IMAGES", tmp_path / "data" / "images" / "items")

    paths.ensure_data_dirs()

    assert (tmp_path / "data" / "raw").is_dir()
    assert (tmp_path / "data" / "processed").is_dir()
    assert (tmp_path / "data" / "images" / "items").is_dir()


def test_relative_to_root_inside(project_root: Path) -> None:
    file_path = project_root / "data" / "raw" / "test.json"
    assert paths.relative_to_root(file_path) == "data/raw/test.json"


def test_relative_to_root_outside(project_root: Path) -> None:
    outside = Path("C:/other/file.txt")
    result = paths.relative_to_root(outside)
    assert "file.txt" in result
