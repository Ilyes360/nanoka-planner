"""Rapport de planification des ascensions armes."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from nanoka.paths import WEAPON_ASCENSION_REPORT_JSON, WEAPON_LOADOUTS_JSON, ensure_data_dirs
from nanoka.report_common import aggregate_totals, load_json, slim_material, write_json

WEAPON_EXP_MATERIALS: list[dict[str, int]] = [
    {"name": "Enhancement Ore", "exp": 400},
    {"name": "Fine Enhancement Ore", "exp": 2_000},
    {"name": "Mystic Enhancement Ore", "exp": 10_000},
]


def build_weapon_report(weapon: dict) -> dict:
    phases_out: list[dict[str, Any]] = []
    for step in weapon.get("ascensions") or []:
        if not isinstance(step, dict):
            continue
        phase = step.get("phase")
        materials = [slim_material(m) for m in step.get("materials") or [] if isinstance(m, dict)]
        mora = int(step.get("cost") or 0)
        phases_out.append(
            {
                "phase": phase,
                "label": f"Ascension {phase}",
                "mora": mora,
                "materials": materials,
                "material_count": len(materials),
            }
        )
    totals, total_mora = aggregate_totals(phases_out)
    return {
        "name": weapon.get("name", ""),
        "id": weapon.get("id", ""),
        "url": weapon.get("url", ""),
        "ascensions": phases_out,
        "totals": totals,
        "total_mora": total_mora,
        "enhancement_exp": {
            "materials": WEAPON_EXP_MATERIALS,
            "mora_per_exp": "1 mora per 10 EXP",
            "note": "Les donnees source ne fournissent pas la courbe d'EXP des armes.",
        },
    }


def build_all_weapon_reports(loadouts: list[dict]) -> list[dict]:
    return sorted(
        [build_weapon_report(w) for w in loadouts if isinstance(w, dict)],
        key=lambda x: str(x.get("name", "")).lower(),
    )


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Rapport de planification des ascensions armes.")
    p.add_argument("--loadouts", type=Path, default=WEAPON_LOADOUTS_JSON)
    p.add_argument("--out", type=Path, default=WEAPON_ASCENSION_REPORT_JSON)
    p.add_argument("--weapon", type=str, default="", help="Filtrer par nom d'arme (partiel, insensible à la casse)")
    p.add_argument("--print", dest="show", action="store_true", help="Afficher le rapport dans le terminal")
    return p.parse_args()


def print_weapon_report(report: dict) -> None:
    print(f"\n{'=' * 60}")
    print(f"{report['name']} (id {report['id']})")
    print(f"{'=' * 60}")
    for step in report.get("ascensions") or []:
        print(f"\n  {step['label']} - {step['mora']:,} mora")
        if not step.get("materials"):
            print("    (aucun materiau d'ascension)")
            continue
        for m in step["materials"]:
            print(f"    x{m['count']:>3}  {m['name']}")
    print(f"\n  Total mora (ascensions) : {report.get('total_mora', 0):,}")
    print("  Cumul materiaux d'ascension :")
    for row in report.get("totals") or []:
        print(f"    x{row['count']:>3}  {row['name']}")
    exp = report.get("enhancement_exp") or {}
    mats = exp.get("materials") or []
    if mats:
        print("\n  Materiaux d'experience d'arme :")
        for row in mats:
            print(f"    {row['name']}: {row['exp']:,} EXP")
        print(f"  Cout mora XP : {exp.get('mora_per_exp', '')}")
        if exp.get("note"):
            print(f"  Note : {exp['note']}")


def main() -> None:
    ensure_data_dirs()
    args = parse_args()
    loadouts = load_json(args.loadouts) if args.loadouts.is_file() else []
    reports = build_all_weapon_reports(loadouts)
    if args.weapon.strip():
        needle = args.weapon.strip().lower()
        reports = [r for r in reports if needle in str(r.get("name", "")).lower()]
    write_json(args.out, reports)
    print(f"Rapport ascension armes : {len(reports)} -> {args.out.resolve()}")
    if args.show:
        if not reports:
            print("Aucune arme trouvee.")
            return
        for report in reports:
            print_weapon_report(report)


if __name__ == "__main__":
    main()
