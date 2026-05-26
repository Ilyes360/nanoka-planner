from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from urllib.request import Request, urlopen

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from nanoka.paths import (
    CHARACTER_IMAGES,
    CHARACTER_ITEMS_JSON,
    CHARACTERS_JSON,
    ITEM_IMAGES,
    ITEMS_JSON,
    WEAPON_IMAGES,
    WEAPON_ITEMS_JSON,
    WEAPONS_JSON,
    ensure_data_dirs,
    relative_to_root,
)

BASE_URL = "https://gi.nanoka.cc/"
CHARACTER_LIST_URL = "https://gi.nanoka.cc/character/"
WEAPON_LIST_URL = "https://gi.nanoka.cc/weapon/"
CHARACTER_STATIC_BASE = "https://static.nanoka.cc/gi/6.5.54/en/character/"
WEAPON_STATIC_BASE = "https://static.nanoka.cc/gi/6.5.54/en/weapon/"
ITEM_INDEX_URL = "https://static.nanoka.cc/gi/6.5.54/en/item_all.json"
ASSET_BASE = "https://static.nanoka.cc/assets/gi/"
WAIT_MS = 1500


@dataclass
class AscensionItem:
    name: str
    quantity: str = ""
    source_text: str = ""


@dataclass
class ScrapedEntry:
    name: str
    type: str
    url: str
    ascension: list[AscensionItem] = field(default_factory=list)
    weapon_ascension: list[AscensionItem] = field(default_factory=list)
    page_facts: list[str] = field(default_factory=list)
    character_images: list[dict[str, str]] = field(default_factory=list)
    weapon_images: list[dict[str, str]] = field(default_factory=list)
    item_images: list[dict[str, str]] = field(default_factory=list)
    item_category: str = ""
    item_sources: list[str] = field(default_factory=list)
    raw_data: dict = field(default_factory=dict)
    notes: str = ""


def get_text(url: str) -> str:
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", "ignore")


def get_json(url: str) -> dict:
    return json.loads(get_text(url))


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.strip().lower()).strip("_") or "unknown"


def extract_ids_from_listing(url: str, kind: str) -> list[str]:
    html = get_text(url)
    return sorted(set(re.findall(rf"/{kind}/(\d+)/?", html)))


def create_chrome_driver(options: Options) -> webdriver.Chrome:
    chrome_bin = os.environ.get("CHROME_BIN", "").strip()
    driver_bin = os.environ.get("CHROMEDRIVER_PATH", "").strip()
    if chrome_bin:
        options.binary_location = chrome_bin
    if driver_bin:
        service = Service(executable_path=driver_bin)
    else:
        service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def extract_ids_with_selenium(url: str, kind: str) -> list[str]:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
    driver = create_chrome_driver(options)
    try:
        driver.get(url)
        driver.implicitly_wait(WAIT_MS / 1000)
        ids: set[str] = set()
        for node in driver.find_elements(By.CSS_SELECTOR, "a[href]"):
            href = node.get_attribute("href") or ""
            match = re.search(rf"/{kind}/(\d+)/?", href)
            if match:
                ids.add(match.group(1))
        return sorted(ids)
    finally:
        driver.quit()


def icon_to_url(icon_name: str) -> str:
    if icon_name.startswith("http://") or icon_name.startswith("https://"):
        return icon_name
    if "." in icon_name.split("/")[-1]:
        return f"{ASSET_BASE}{icon_name}"
    return f"{ASSET_BASE}{icon_name}.webp"


def image_filename(image_url: str) -> str:
    ext = Path(image_url).suffix.lower() or ".img"
    digest = hashlib.sha1(image_url.encode("utf-8")).hexdigest()[:16]
    return f"{digest}{ext}"


def download(url: str, target: Path) -> bool:
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urlopen(req, timeout=30) as resp:
            target.write_bytes(resp.read())
        return True
    except Exception:
        return False


def collect_icon_names(payload: object, out: set[str]) -> None:
    if isinstance(payload, dict):
        for k, v in payload.items():
            if k == "icon" and isinstance(v, str) and v.strip():
                out.add(v.strip())
            else:
                collect_icon_names(v, out)
    elif isinstance(payload, list):
        for v in payload:
            collect_icon_names(v, out)


def expand_character_icons(data: dict) -> set[str]:
    out: set[str] = set()
    base_icon = str(data.get("icon", "")).strip()
    if base_icon.startswith("UI_AvatarIcon_"):
        suffix = base_icon.removeprefix("UI_AvatarIcon_")
        out.update(
            {
                f"UI_Gacha_AvatarImg_{suffix}",
                f"UI_Gacha_AvatarImg_{suffix}_P",
                f"UI_Gacha_AvatarImg_{suffix}_Large",
                f"UI_AvatarIcon_Side_{suffix}",
            }
        )
    info = data.get("chara_info", {})
    if isinstance(info, dict):
        for costume in info.get("costume", []):
            if not isinstance(costume, dict):
                continue
            icon = str(costume.get("icon", "")).strip()
            if not icon:
                continue
            out.add(icon)
            if icon.startswith("UI_AvatarIcon_"):
                suffix = icon.removeprefix("UI_AvatarIcon_")
                out.update(
                    {
                        f"UI_Gacha_AvatarImg_{suffix}",
                        f"UI_Gacha_AvatarImg_{suffix}_P",
                        f"UI_Gacha_AvatarImg_{suffix}_Large",
                        f"UI_Costume_{suffix}",
                        f"UI_AvatarIcon_Side_{suffix}",
                    }
                )
    return out


def collect_images(icon_names: set[str], entry_id: str, entry_name: str, out_dir: Path, with_download: bool) -> list[dict[str, str]]:
    target_dir = out_dir / f"{entry_id}_{slugify(entry_name)}"
    if with_download:
        target_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    for i, icon in enumerate(sorted(icon_names), start=1):
        url = icon_to_url(icon)
        if url in seen:
            continue
        seen.add(url)
        rec = {"url": url, "alt": icon.replace("_", " ")}
        if with_download:
            name = f"{i:03d}_{slugify(rec['alt'])[:40]}_{image_filename(url)}"
            path = target_dir / name
            if not path.exists() and not download(url, path):
                continue
            rec["local_path"] = relative_to_root(path)
        rows.append(rec)
    return rows


def dedupe(items: list[AscensionItem]) -> list[AscensionItem]:
    out: list[AscensionItem] = []
    seen: set[tuple[str, str, str]] = set()
    for m in items:
        k = (m.name.lower(), m.quantity, m.source_text.lower())
        if k in seen:
            continue
        seen.add(k)
        out.append(m)
    return out


def parse_character(char_id: str, data: dict, img_dir: Path, dl: bool) -> ScrapedEntry:
    name = str(data.get("name", "")).strip() or f"character_{char_id}"
    mats = data.get("materials", {})
    asc: list[AscensionItem] = []
    for step in mats.get("ascensions", []):
        for mat in step.get("mats", []):
            n, q = str(mat.get("name", "")).strip(), str(mat.get("count", ""))
            if n:
                asc.append(AscensionItem(name=n, quantity=q, source_text=f"{n} {q}".strip()))
    for track in mats.get("talents", []):
        for step in track:
            for mat in step.get("mats", []):
                n, q = str(mat.get("name", "")).strip(), str(mat.get("count", ""))
                if n:
                    asc.append(AscensionItem(name=n, quantity=q, source_text=f"{n} {q}".strip()))
    icons: set[str] = set()
    collect_icon_names(data, icons)
    icons.update(expand_character_icons(data))
    images = collect_images(icons, char_id, name, img_dir, dl)
    info = data.get("chara_info", {})
    facts = [str(info.get("vision", "")).strip(), str(data.get("weapon", "")).replace("WEAPON_", "").replace("_", " ").strip(), str(info.get("title", "")).strip()]
    return ScrapedEntry(name=name, type="character", url=f"{BASE_URL}character/{char_id}", ascension=dedupe(asc), page_facts=[f for f in facts if f], character_images=images, raw_data=data)


def parse_weapon(weapon_id: str, data: dict, img_dir: Path, dl: bool) -> ScrapedEntry:
    name = str(data.get("name", "")).strip() or f"weapon_{weapon_id}"
    mats = data.get("materials", {})
    asc: list[AscensionItem] = []
    if isinstance(mats, dict):
        for _, step in sorted(mats.items(), key=lambda x: str(x[0])):
            if not isinstance(step, dict):
                continue
            for mat in step.get("mats", []):
                n, q = str(mat.get("name", "")).strip(), str(mat.get("count", ""))
                if n:
                    asc.append(AscensionItem(name=n, quantity=q, source_text=f"{n} {q}".strip()))
    icons: set[str] = set()
    collect_icon_names(data, icons)
    images = collect_images(icons, weapon_id, name, img_dir, dl)
    facts = [str(data.get("weapon_type", "")).replace("WEAPON_", "").replace("_", " ").strip(), f"Rarity: {data.get('rarity', '')}"]
    return ScrapedEntry(name=name, type="weapon", url=f"{BASE_URL}weapon/{weapon_id}", weapon_ascension=dedupe(asc), page_facts=[f for f in facts if f and f != "Rarity: "], weapon_images=images, raw_data=data)


def parse_items(item_all: dict, img_dir: Path, dl: bool, max_items: int) -> list[ScrapedEntry]:
    rows = sorted(item_all.items(), key=lambda r: int(r[0]) if r[0].isdigit() else r[0])
    if max_items > 0:
        rows = rows[:max_items]
    out: list[ScrapedEntry] = []
    for item_id, data in rows:
        if not isinstance(data, dict):
            continue
        name = str(data.get("name", "")).strip() or f"item_{item_id}"
        icon = str(data.get("icon", "")).strip()
        images = collect_images({icon} if icon else set(), str(item_id), name, img_dir, dl) if icon else []
        out.append(
            ScrapedEntry(
                name=name,
                type="item",
                url=f"{BASE_URL}item/{item_id}",
                page_facts=[str(data.get("type", "")).strip(), str(data.get("item_type", "")).strip()],
                item_images=images,
                item_category=str(data.get("type", "")).strip(),
                item_sources=[str(s).strip() for s in data.get("source_list", []) if str(s).strip()],
                raw_data=data,
                notes=f"Source: {ITEM_INDEX_URL}",
            )
        )
    return out


def export_all(entries: list[ScrapedEntry], chars_out: Path, weapons_out: Path, items_out: Path, char_items_out: Path, weapon_items_out: Path) -> None:
    chars, weapons, items = [], [], []
    char_idx: dict[str, dict] = {}
    weapon_idx: dict[str, dict] = {}
    for e in entries:
        row = {
            "name": e.name,
            "url": e.url,
            "page_facts": sorted([f for f in e.page_facts if f], key=str.lower),
            "character_images": sorted(e.character_images, key=lambda x: x.get("url", "")),
            "weapon_images": sorted(e.weapon_images, key=lambda x: x.get("url", "")),
            "item_images": sorted(e.item_images, key=lambda x: x.get("url", "")),
            "item_category": e.item_category,
            "item_sources": sorted(e.item_sources, key=str.lower),
            "raw_data": e.raw_data,
            "notes": e.notes,
            "ascension": [asdict(x) for x in e.ascension],
            "weapon_ascension": [asdict(x) for x in e.weapon_ascension],
        }
        if e.type == "character":
            chars.append(row)
        elif e.type == "weapon":
            weapons.append(row)
        else:
            items.append(row)
        for scope, mats, idx in (("character", e.ascension, char_idx), ("weapon", e.weapon_ascension, weapon_idx)):
            for m in mats:
                key = m.name.strip().lower()
                if not key:
                    continue
                if key not in idx:
                    idx[key] = {"name": m.name, "seen_quantities": [], "source_texts": [], "used_by": []}
                if m.quantity and m.quantity not in idx[key]["seen_quantities"]:
                    idx[key]["seen_quantities"].append(m.quantity)
                if m.source_text and m.source_text not in idx[key]["source_texts"]:
                    idx[key]["source_texts"].append(m.source_text)
    for path, payload in (
        (chars_out, chars),
        (weapons_out, weapons),
        (items_out, items),
        (char_items_out, list(char_idx.values())),
        (weapon_items_out, list(weapon_idx.values())),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        key_fn = (lambda x: x["name"].lower()) if payload and "name" in payload[0] else str
        path.write_text(json.dumps(sorted(payload, key=key_fn), ensure_ascii=False, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Fetch character/weapon/item data from static.nanoka.cc endpoints.")
    p.add_argument("--max-characters", type=int, default=0)
    p.add_argument("--max-weapons", type=int, default=0)
    p.add_argument("--max-items", type=int, default=0)
    p.add_argument("--skip-image-download", action="store_true")
    p.add_argument("--character-images-dir", type=Path, default=CHARACTER_IMAGES)
    p.add_argument("--weapon-images-dir", type=Path, default=WEAPON_IMAGES)
    p.add_argument("--item-images-dir", type=Path, default=ITEM_IMAGES)
    p.add_argument("--characters-json-out", type=Path, default=CHARACTERS_JSON)
    p.add_argument("--weapons-json-out", type=Path, default=WEAPONS_JSON)
    p.add_argument("--items-json-out", type=Path, default=ITEMS_JSON)
    p.add_argument("--character-items-json-out", type=Path, default=CHARACTER_ITEMS_JSON)
    p.add_argument("--weapon-items-json-out", type=Path, default=WEAPON_ITEMS_JSON)
    return p.parse_args()


def main() -> None:
    ensure_data_dirs()
    args = parse_args()
    dl = not args.skip_image_download

    char_ids = extract_ids_from_listing(CHARACTER_LIST_URL, "character")
    weapon_ids = extract_ids_from_listing(WEAPON_LIST_URL, "weapon")
    if not char_ids:
        char_ids = extract_ids_with_selenium(CHARACTER_LIST_URL, "character")
    if not weapon_ids:
        weapon_ids = extract_ids_with_selenium(WEAPON_LIST_URL, "weapon")
    if args.max_characters > 0:
        char_ids = char_ids[: args.max_characters]
    if args.max_weapons > 0:
        weapon_ids = weapon_ids[: args.max_weapons]

    entries: list[ScrapedEntry] = []
    print(f"Characters found: {len(char_ids)}")
    for i, char_id in enumerate(char_ids, start=1):
        try:
            entries.append(parse_character(char_id, get_json(f"{CHARACTER_STATIC_BASE}{char_id}.json"), args.character_images_dir, dl))
            print(f"[C {i}/{len(char_ids)}] {char_id}")
        except Exception as exc:
            entries.append(ScrapedEntry(name="Unknown", type="character", url=f"{BASE_URL}character/{char_id}", notes=f"Failed: {exc}"))

    print(f"Weapons found: {len(weapon_ids)}")
    for i, weapon_id in enumerate(weapon_ids, start=1):
        try:
            entries.append(parse_weapon(weapon_id, get_json(f"{WEAPON_STATIC_BASE}{weapon_id}.json"), args.weapon_images_dir, dl))
            print(f"[W {i}/{len(weapon_ids)}] {weapon_id}")
        except Exception as exc:
            entries.append(ScrapedEntry(name="Unknown", type="weapon", url=f"{BASE_URL}weapon/{weapon_id}", notes=f"Failed: {exc}"))

    item_all = get_json(ITEM_INDEX_URL)
    item_entries = parse_items(item_all, args.item_images_dir, dl, args.max_items)
    entries.extend(item_entries)
    print(f"Items parsed: {len(item_entries)}")

    export_all(
        entries,
        chars_out=args.characters_json_out,
        weapons_out=args.weapons_json_out,
        items_out=args.items_json_out,
        char_items_out=args.character_items_json_out,
        weapon_items_out=args.weapon_items_json_out,
    )
    print(f"Characters JSON: {args.characters_json_out.resolve()}")
    print(f"Weapons JSON: {args.weapons_json_out.resolve()}")
    print(f"Items JSON: {args.items_json_out.resolve()}")


if __name__ == "__main__":
    main()
