"""Met à jour les chemins local_path dans les JSON (réorganisation data/images/)."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from paths import LEGACY_IMAGE_DIRS, RAW, ROOT

_LOCAL_PATH_RE = re.compile(r'"local_path": "([^"]*)"')


def normalize_local_path(value: str) -> str:
    out = value
    for old_name, new_dir in LEGACY_IMAGE_DIRS.items():
        new_prefix = new_dir.relative_to(ROOT).as_posix()
        out = out.replace(f"{old_name}/", f"{new_prefix}/")
        out = out.replace(f"{old_name}\\", f"{new_prefix}/")
        out = out.replace(old_name, f"{new_prefix}/")
    for kind in ("characters", "weapons", "items"):
        out = out.replace(f"data/images/{kind}/\\", f"data/images/{kind}/")
    out = out.replace("\\", "/")
    while "//" in out:
        out = out.replace("//", "/")
    return out


def rewrite_file(path: Path, dry_run: bool = False) -> int:
    if not path.is_file():
        return 0
    text = path.read_text(encoding="utf-8")
    original = text

    def repl(match: re.Match[str]) -> str:
        fixed = normalize_local_path(match.group(1))
        return '"local_path": ' + json.dumps(fixed, ensure_ascii=False)

    text = _LOCAL_PATH_RE.sub(repl, text)

    if text == original:
        return 0
    if not dry_run:
        path.write_text(text, encoding="utf-8")
        json.loads(path.read_text(encoding="utf-8"))
    return 1


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Réécrit les chemins d'images dans les JSON.")
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    targets = list(RAW.glob("*.json"))
    updated = 0
    for f in targets:
        try:
            if rewrite_file(f, dry_run=args.dry_run):
                updated += 1
                print(f"OK: {f.name}")
        except Exception as exc:
            print(f"ERREUR {f.name}: {exc}")
    print(f"Fichiers mis à jour: {updated}/{len(targets)} (dry_run={args.dry_run})")


if __name__ == "__main__":
    main()
