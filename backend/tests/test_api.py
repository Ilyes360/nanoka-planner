"""Tests pour l'API FastAPI."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from nanoka.api import _is_displayable, app
from nanoka.media import pick_character_avatar_file as _pick_character_avatar_file
from nanoka.media import pick_character_splash_file as _pick_character_splash_file


def _patch_data_paths(monkeypatch: pytest.MonkeyPatch, **paths: Path) -> None:
    from nanoka import data_store, media, paths as paths_mod

    for name, value in paths.items():
        monkeypatch.setattr(paths_mod, name, value)
        if hasattr(data_store, name):
            monkeypatch.setattr(data_store, name, value)
        if hasattr(media, name):
            monkeypatch.setattr(media, name, value)
    data_store.clear_caches()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_is_displayable_filters_unknown() -> None:
    assert _is_displayable({"name": "Aino"}) is True
    assert _is_displayable({"name": "Unknown"}) is False
    assert _is_displayable({"name": " unknown "}) is False


def test_list_characters_hides_unknown(
    client: TestClient, sample_character_raw: dict, item_lookup, tmp_path: Path, monkeypatch
) -> None:
    from nanoka import assign

    by_id, by_name = item_lookup
    good = assign.character_loadout(sample_character_raw, by_id, by_name)
    bad = {**good, "name": "Unknown", "id": "99999999", "url": "https://gi.nanoka.cc/character/99999999"}
    loadouts_path = tmp_path / "character_loadouts.json"
    loadouts_path.write_text(json.dumps([good, bad]), encoding="utf-8")
    _patch_data_paths(
        monkeypatch,
        CHARACTER_LOADOUTS_JSON=loadouts_path,
        CHARACTER_IMAGES=tmp_path / "images" / "characters",
    )

    data = client.get("/api/characters").json()
    assert len(data) == 1
    assert data[0]["name"] == "Tester"
    assert client.get("/api/characters/99999999").status_code == 404


def test_pick_character_splash_prefers_gacha(tmp_path: Path) -> None:
    folder = tmp_path / "10000099_tester"
    folder.mkdir()
    (folder / "010_ui_gacha_avatarimg_tester.webp").write_bytes(b"x")
    (folder / "010_ui_gacha_avatarimg_tester_p.webp").write_bytes(b"x")
    (folder / "005_ui_avataricon_tester.webp").write_bytes(b"x")
    picked = _pick_character_splash_file(folder)
    assert picked is not None
    assert "gacha_avatarimg" in picked.name


def test_pick_character_avatar_prefers_avataricon(tmp_path: Path) -> None:
    folder = tmp_path / "10000099_tester"
    folder.mkdir()
    (folder / "001_skill_a_01.webp").write_bytes(b"x")
    (folder / "005_ui_avataricon_tester.webp").write_bytes(b"x")
    (folder / "006_ui_avataricon_side_tester.webp").write_bytes(b"x")
    (folder / "007_ui_avataricon_testercostume.webp").write_bytes(b"x")
    picked = _pick_character_avatar_file(folder)
    assert picked is not None
    assert picked.name == "005_ui_avataricon_tester.webp"


def test_list_characters_uses_avatar_icon(
    client: TestClient, sample_character_raw: dict, item_lookup, tmp_path: Path, monkeypatch
) -> None:
    from nanoka import assign

    by_id, by_name = item_lookup
    loadout = assign.character_loadout(sample_character_raw, by_id, by_name)
    loadouts_path = tmp_path / "character_loadouts.json"
    loadouts_path.write_text(json.dumps([loadout]), encoding="utf-8")
    char_dir = tmp_path / "images" / "characters" / "10000099_tester"
    char_dir.mkdir(parents=True)
    (char_dir / "001_skill.webp").write_bytes(b"x")
    (char_dir / "002_ui_avataricon_tester.webp").write_bytes(b"x")
    _patch_data_paths(
        monkeypatch,
        CHARACTER_LOADOUTS_JSON=loadouts_path,
        CHARACTER_IMAGES=tmp_path / "images" / "characters",
        IMAGES=tmp_path / "images",
    )

    data = client.get("/api/characters").json()
    assert data[0]["icon_url"] == "/media/characters/10000099_tester/002_ui_avataricon_tester.webp"


def test_health(client: TestClient) -> None:
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_security_headers_present(client: TestClient) -> None:
    res = client.get("/api/health")
    assert res.headers["x-content-type-options"] == "nosniff"
    assert res.headers["x-frame-options"] == "DENY"
    assert res.headers["referrer-policy"] == "no-referrer"
    assert "default-src 'none'" in res.headers["content-security-policy"]


def test_cors_allows_dev_origin(client: TestClient) -> None:
    res = client.options(
        "/api/characters",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert res.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_list_characters(client: TestClient, sample_character_raw: dict, item_lookup, tmp_path: Path, monkeypatch) -> None:
    from nanoka import assign

    by_id, by_name = item_lookup
    loadout = assign.character_loadout(sample_character_raw, by_id, by_name)
    loadouts_path = tmp_path / "character_loadouts.json"
    loadouts_path.write_text(json.dumps([loadout]), encoding="utf-8")
    img_dir = tmp_path / "images" / "characters"
    _patch_data_paths(
        monkeypatch,
        CHARACTER_LOADOUTS_JSON=loadouts_path,
        CHARACTER_IMAGES=img_dir,
    )

    res = client.get("/api/characters")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["name"] == "Tester"


def test_character_detail_404(client: TestClient) -> None:
    assert client.get("/api/characters/99999999").status_code == 404


def test_character_detail_talent_levels_plan(
    client: TestClient, sample_character_raw: dict, item_lookup, tmp_path: Path, monkeypatch
) -> None:
    from nanoka import assign

    by_id, by_name = item_lookup
    loadout = assign.character_loadout(sample_character_raw, by_id, by_name)
    loadouts_path = tmp_path / "character_loadouts.json"
    loadouts_path.write_text(json.dumps([loadout]), encoding="utf-8")
    chars_path = tmp_path / "characters.json"
    chars_path.write_text(json.dumps([sample_character_raw]), encoding="utf-8")
    _patch_data_paths(
        monkeypatch,
        CHARACTER_LOADOUTS_JSON=loadouts_path,
        CHARACTERS_JSON=chars_path,
    )

    res = client.get(f"/api/characters/{loadout['id']}?talent_levels=1,1,1")
    assert res.status_code == 200
    body = res.json()
    assert "talents_plan" in body
    assert body["talents_plan"]["total"]["total_mora"] == 0
    assert body["talents_plan"]["total"]["materials"] == []
    assert body["talents"]["level_range"]["min"] == 1


def test_character_detail_includes_profile(
    client: TestClient, sample_character_raw: dict, item_lookup, tmp_path: Path, monkeypatch
) -> None:
    from nanoka import assign

    raw = dict(sample_character_raw)
    raw["raw_data"] = {
        **raw["raw_data"],
        "desc": "A test character.",
        "element": "Geo",
        "weapon": "WEAPON_SWORD_ONE_HAND",
        "chara_info": {
            "title": "Test Title",
            "vision": "Geo",
            "region": "ASSOC_TYPE_LIYUE",
            "constellation": "Test Const",
        },
    }
    by_id, by_name = item_lookup
    loadout = assign.character_loadout(raw, by_id, by_name)
    loadouts_path = tmp_path / "character_loadouts.json"
    loadouts_path.write_text(json.dumps([loadout]), encoding="utf-8")
    chars_path = tmp_path / "characters.json"
    chars_path.write_text(json.dumps([raw]), encoding="utf-8")
    _patch_data_paths(
        monkeypatch,
        CHARACTER_LOADOUTS_JSON=loadouts_path,
        CHARACTERS_JSON=chars_path,
    )

    body = client.get(f"/api/characters/{loadout['id']}").json()
    assert body["title"] == "Test Title"
    assert body["vision"] == "Geo"
    assert body["element"] == "Geo"
    assert body["weapon_type"] == "Sword"
    assert body["region"] == "Liyue"
    assert body["constellation"] == "Test Const"
    assert "test character" in body["description"].lower()


def test_weapon_detail_includes_profile(
    client: TestClient, sample_weapon_raw: dict, item_lookup, tmp_path: Path, monkeypatch
) -> None:
    from nanoka import assign

    raw = dict(sample_weapon_raw)
    raw["raw_data"] = {
        **raw["raw_data"],
        "desc": "A test weapon.",
        "weapon_type": "WEAPON_SWORD_ONE_HAND",
        "rarity": 4,
    }
    by_id, by_name = item_lookup
    loadout = assign.weapon_loadout(raw, by_id, by_name)
    loadouts_path = tmp_path / "weapon_loadouts.json"
    loadouts_path.write_text(json.dumps([loadout]), encoding="utf-8")
    weapons_path = tmp_path / "weapons.json"
    weapons_path.write_text(json.dumps([raw]), encoding="utf-8")
    _patch_data_paths(
        monkeypatch,
        WEAPON_LOADOUTS_JSON=loadouts_path,
        WEAPONS_JSON=weapons_path,
    )

    body = client.get(f"/api/weapons/{loadout['id']}").json()
    assert body["weapon_type"] == "Sword"
    assert body["rarity"] == "4★"
    assert "test weapon" in body["description"].lower()
