"""Rapport de planification des talents personnages."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from nanoka.paths import CHARACTER_LOADOUTS_JSON, CHARACTER_TALENT_REPORT_JSON, ensure_data_dirs
from nanoka.report_common import aggregate_totals, load_json, slim_material, write_json

TALENT_MIN_LEVEL = 2
TALENT_MAX_LEVEL = 10


def build_talent_report(char: dict) -> dict:
    tracks_out: list[dict[str, Any]] = []
    all_levels: list[dict[str, Any]] = []
    for track in char.get("talents") or []:
        if not isinstance(track, dict):
            continue
        track_idx = int(track.get("track") or 0)
        levels_out: list[dict[str, Any]] = []
        for level in track.get("levels") or []:
            if not isinstance(level, dict):
                continue
            raw_level_idx = int(level.get("level") or 0)
            target_level = raw_level_idx + 1
            if target_level < TALENT_MIN_LEVEL or target_level > TALENT_MAX_LEVEL:
                continue
            materials = [slim_material(m) for m in level.get("materials") or [] if isinstance(m, dict)]
            mora = int(level.get("cost") or 0)
            row = {
                "track": track_idx,
                "level": target_level,
                "label": f"Talent {track_idx} - niveau {target_level}",
                "mora": mora,
                "materials": materials,
                "material_count": len(materials),
            }
            levels_out.append(row)
            all_levels.append(row)
        track_totals, track_total_mora = aggregate_totals(levels_out)
        tracks_out.append(
            {
                "track": track_idx,
                "levels": levels_out,
                "totals": track_totals,
                "total_mora": track_total_mora,
                "level_count": len(levels_out),
            }
        )
    totals, total_mora = aggregate_totals(all_levels)
    return {
        "name": char.get("name", ""),
        "id": char.get("id", ""),
        "url": char.get("url", ""),
        "talents": tracks_out,
        "totals": totals,
        "total_mora": total_mora,
        "level_count": len(all_levels),
        "level_range": {"min": TALENT_MIN_LEVEL, "max": TALENT_MAX_LEVEL},
    }


def build_all_talent_reports(loadouts: list[dict]) -> list[dict]:
    return sorted(
        [build_talent_report(c) for c in loadouts if isinstance(c, dict)],
        key=lambda x: str(x.get("name", "")).lower(),
    )


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Rapport de planification des talents personnages.")
    p.add_argument("--loadouts", type=Path, default=CHARACTER_LOADOUTS_JSON)
    p.add_argument("--out", type=Path, default=CHARACTER_TALENT_REPORT_JSON)
    p.add_argument("--character", type=str, default="", help="Filtrer par nom (partiel, insensible à la casse)")
    p.add_argument("--print", dest="show", action="store_true", help="Afficher le rapport dans le terminal")
    return p.parse_args()


def print_talent_report(report: dict) -> None:
    print(f"\n{'=' * 60}")
    print(f"{report['name']} (id {report['id']})")
    print(f"{'=' * 60}")
    for track in report.get("talents") or []:
        print(f"\n  Talent {track['track']} - total {track.get('total_mora', 0):,} mora")
        for level in track.get("levels") or []:
            print(f"    Niveau {level['level']} - {level['mora']:,} mora")
            if not level.get("materials"):
                print("      (aucun materiau)")
                continue
            for m in level["materials"]:
                print(f"      x{m['count']:>3}  {m['name']}")
        if track.get("totals"):
            print("    Cumul materiaux (talent) :")
            for row in track["totals"]:
                print(f"      x{row['count']:>3}  {row['name']}")
    print(f"\n  Total mora (talents) : {report.get('total_mora', 0):,}")
    print("  Cumul materiaux (tous talents) :")
    for row in report.get("totals") or []:
        print(f"    x{row['count']:>3}  {row['name']}")


def main() -> None:
    ensure_data_dirs()
    args = parse_args()
    loadouts = load_json(args.loadouts) if args.loadouts.is_file() else []
    reports = build_all_talent_reports(loadouts)
    if args.character.strip():
        needle = args.character.strip().lower()
        reports = [r for r in reports if needle in str(r.get("name", "")).lower()]
    write_json(args.out, reports)
    print(f"Rapport talents personnages : {len(reports)} -> {args.out.resolve()}")
    if args.show:
        if not reports:
            print("Aucun personnage trouve.")
            return
        for report in reports:
            print_talent_report(report)


if __name__ == "__main__":
    main()
