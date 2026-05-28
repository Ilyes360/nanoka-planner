"""Rapport de planification des ascensions personnages."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from nanoka.exp_books import exp_block
from nanoka.report_common import load_json, slim_material, write_json
from nanoka.paths import (
    CHARACTER_ASCENSION_REPORT_JSON,
    CHARACTER_LOADOUTS_JSON,
    CHARACTERS_JSON,
    ensure_data_dirs,
)

# Phases d'ascension Genshin (6 paliers jusqu'au niv. 90)
ASCENSION_PHASES: list[dict[str, int | str]] = [
    {"phase": 1, "at_level": 20, "new_level_cap": 40},
    {"phase": 2, "at_level": 40, "new_level_cap": 50},
    {"phase": 3, "at_level": 50, "new_level_cap": 60},
    {"phase": 4, "at_level": 60, "new_level_cap": 70},
    {"phase": 5, "at_level": 70, "new_level_cap": 80},
    {"phase": 6, "at_level": 80, "new_level_cap": 90},
]

def phase_meta(phase: int) -> dict[str, int | str]:
    for row in ASCENSION_PHASES:
        if row["phase"] == phase:
            return row
    return {"phase": phase, "at_level": 0, "new_level_cap": 0}


def prev_ascension_level(phase: int) -> int:
    if phase <= 1:
        return 1
    return int(phase_meta(phase - 1)["at_level"])


def index_level_exp_by_id(characters: list[dict]) -> dict[str, list[int]]:
    out: dict[str, list[int]] = {}
    for row in characters:
        if not isinstance(row, dict):
            continue
        cid = str(row.get("url", "")).split("/character/")[-1].split("/")[0]
        if not cid.isdigit():
            continue
        raw = row.get("raw_data") or {}
        level_exp = raw.get("level_exp")
        if isinstance(level_exp, list) and level_exp:
            out[cid] = [int(x) for x in level_exp]
    return out


def resolve_level_exp(char: dict, level_exp_index: dict[str, list[int]]) -> list[int]:
    embedded = char.get("level_exp")
    if isinstance(embedded, list) and embedded:
        return [int(x) for x in embedded]
    cid = str(char.get("id", "")).strip()
    return level_exp_index.get(cid, [])


def build_character_report(char: dict, level_exp_index: dict[str, list[int]] | None = None) -> dict:
    level_exp_index = level_exp_index or {}
    level_exp = resolve_level_exp(char, level_exp_index)

    phases_out: list[dict] = []
    exp_book_totals: dict[str, int] = {}

    for step in char.get("ascensions") or []:
        if not isinstance(step, dict):
            continue
        phase = int(step.get("phase") or 0)
        meta = phase_meta(phase)
        materials = [slim_material(m) for m in step.get("materials") or [] if isinstance(m, dict)]
        mora = int(step.get("cost") or 0)
        from_level = prev_ascension_level(phase)
        to_level = int(meta["at_level"])
        exp_info = exp_block(level_exp, from_level, to_level) if level_exp else None
        if exp_info:
            for b in exp_info.get("books", []):
                exp_book_totals[b["name"]] = exp_book_totals.get(b["name"], 0) + b["count"]

        phase_row: dict[str, Any] = {
            "phase": phase,
            "label": f"Ascension {phase} (niv. {meta['at_level']} -> {meta['new_level_cap']})",
            "at_level": meta["at_level"],
            "new_level_cap": meta["new_level_cap"],
            "mora": mora,
            "materials": materials,
            "material_count": len(materials),
        }
        if exp_info:
            phase_row["leveling"] = {
                "label": f"Montee {from_level} -> {to_level} (avant ascension)",
                **exp_info,
            }
        phases_out.append(phase_row)

    max_level = int(ASCENSION_PHASES[-1]["new_level_cap"]) if ASCENSION_PHASES else 90
    exp_to_max = exp_block(level_exp, 1, max_level) if level_exp else None
    totals: dict[str, int] = {}
    total_mora = 0
    for step in phases_out:
        total_mora += int(step.get("mora") or 0)
        for mat in step.get("materials") or []:
            key = str(mat.get("name", "")).strip()
            if not key:
                continue
            totals[key] = totals.get(key, 0) + int(mat.get("count") or 0)

    return {
        "name": char.get("name", ""),
        "id": char.get("id", ""),
        "url": char.get("url", ""),
        "ascensions": phases_out,
        "totals": [{"name": n, "count": c} for n, c in sorted(totals.items(), key=lambda x: x[0].lower())],
        "total_mora": total_mora,
        "exp_books_total": [
            {"name": n, "count": c} for n, c in sorted(exp_book_totals.items(), key=lambda x: x[0].lower())
        ],
        "exp_to_level_90": exp_to_max,
    }


def build_all_reports(loadouts: list[dict], level_exp_index: dict[str, list[int]] | None = None) -> list[dict]:
    return sorted(
        [build_character_report(c, level_exp_index) for c in loadouts if isinstance(c, dict)],
        key=lambda x: str(x.get("name", "")).lower(),
    )

def print_character_report(report: dict) -> None:
    print(f"\n{'=' * 60}")
    print(f"{report['name']} (id {report['id']})")
    print(f"{'=' * 60}")
    for step in report.get("ascensions") or []:
        print(f"\n  {step['label']} - {step['mora']:,} mora")
        leveling = step.get("leveling")
        if leveling:
            print(
                f"    EXP {leveling['from_level']}->{leveling['to_level']}: "
                f"{leveling['total_exp']:,} ({leveling['book_count']} livres)"
            )
            for b in leveling.get("books", []):
                print(f"      x{b['count']:>3}  {b['name']}")
            if leveling.get("remainder_exp"):
                print(f"      (reste {leveling['remainder_exp']:,} EXP non couvert par les livres)")
        if not step["materials"]:
            print("    (aucun materiau d'ascension)")
        else:
            for m in step["materials"]:
                print(f"    x{m['count']:>3}  {m['name']}")
    exp90 = report.get("exp_to_level_90")
    if exp90:
        print(f"\n  Total 1->{exp90['to_level']} : {exp90['total_exp']:,} EXP")
        for b in exp90.get("books", []):
            print(f"    x{b['count']:>3}  {b['name']}")
    if report.get("exp_books_total"):
        print("\n  Cumul livres d'EXP (toutes montees) :")
        for row in report["exp_books_total"]:
            print(f"    x{row['count']:>3}  {row['name']}")
    print(f"\n  Total mora (ascensions) : {report.get('total_mora', 0):,}")
    print("  Cumul materiaux d'ascension :")
    for row in report.get("totals") or []:
        print(f"    x{row['count']:>3}  {row['name']}")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Rapport de planification des ascensions personnages.")
    p.add_argument("--loadouts", type=Path, default=CHARACTER_LOADOUTS_JSON)
    p.add_argument("--characters", type=Path, default=CHARACTERS_JSON, help="JSON bruts (level_exp)")
    p.add_argument("--out", type=Path, default=CHARACTER_ASCENSION_REPORT_JSON)
    p.add_argument("--character", type=str, default="", help="Filtrer par nom (partiel, insensible à la casse)")
    p.add_argument("--print", dest="show", action="store_true", help="Afficher le rapport dans le terminal")
    return p.parse_args()


def main() -> None:
    ensure_data_dirs()
    args = parse_args()
    loadouts = load_json(args.loadouts)
    characters = load_json(args.characters) if args.characters.is_file() else []
    level_exp_index = index_level_exp_by_id(characters) if characters else {}
    reports = build_all_reports(loadouts, level_exp_index)

    if args.character.strip():
        needle = args.character.strip().lower()
        reports = [r for r in reports if needle in str(r.get("name", "")).lower()]

    write_json(args.out, reports)
    print(f"Rapport ascension personnages : {len(reports)} -> {args.out.resolve()}")

    if args.show:
        if reports:
            for report in reports:
                print_character_report(report)
        else:
            print("Aucun personnage trouve.")


if __name__ == "__main__":
    main()
