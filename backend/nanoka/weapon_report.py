"""Rapport de planification des ascensions armes."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from nanoka.ascension_report import ASCENSION_PHASES, phase_meta, prev_ascension_level
from nanoka.weapon_exp import WEAPON_ENHANCEMENT_ORES, parse_level_exp, weapon_exp_block
from nanoka.paths import (
    WEAPON_ASCENSION_REPORT_JSON,
    WEAPON_LOADOUTS_JSON,
    WEAPONS_JSON,
    ensure_data_dirs,
)
from nanoka.report_common import aggregate_totals, load_json, slim_material, write_json


def index_weapon_level_exp(weapons: list[dict]) -> dict[str, list[int]]:
    out: dict[str, list[int]] = {}
    for row in weapons:
        if not isinstance(row, dict):
            continue
        wid = str(row.get("url", "")).split("/weapon/")[-1].split("/")[0]
        if not wid.isdigit():
            continue
        raw = row.get("raw_data") or row
        level_exp = parse_level_exp(raw if isinstance(raw, dict) else {})
        if level_exp:
            out[wid] = level_exp
    return out


def resolve_level_exp(weapon: dict, level_exp_index: dict[str, list[int]]) -> list[int]:
    embedded = weapon.get("level_exp")
    if isinstance(embedded, list) and embedded:
        return [int(x) for x in embedded]
    wid = str(weapon.get("id", "")).strip()
    return level_exp_index.get(wid, [])


def _accumulate_leveling(
    exp_info: dict,
    ore_totals: dict[str, int],
    leveling_mora_total: int,
) -> int:
    leveling_mora_total += int(exp_info.get("mora_cost") or 0)
    for ore in exp_info.get("ores") or []:
        ore_totals[ore["name"]] = ore_totals.get(ore["name"], 0) + ore["count"]
    return leveling_mora_total


def build_weapon_report(weapon: dict, level_exp_index: dict[str, list[int]] | None = None) -> dict:
    level_exp_index = level_exp_index or {}
    level_exp = resolve_level_exp(weapon, level_exp_index)

    phases_out: list[dict[str, Any]] = []
    ore_totals: dict[str, int] = {}
    leveling_mora_total = 0

    for step in weapon.get("ascensions") or []:
        if not isinstance(step, dict):
            continue
        phase = int(step.get("phase") or 0)
        meta = phase_meta(phase)
        materials = [slim_material(m) for m in step.get("materials") or [] if isinstance(m, dict)]
        mora = int(step.get("cost") or 0)
        from_level = prev_ascension_level(phase)
        to_level = int(meta["at_level"])
        exp_info = weapon_exp_block(level_exp, from_level, to_level) if level_exp else None
        if exp_info:
            leveling_mora_total = _accumulate_leveling(exp_info, ore_totals, leveling_mora_total)

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

    totals, total_mora = aggregate_totals(phases_out)
    max_level = int(ASCENSION_PHASES[-1]["new_level_cap"]) if ASCENSION_PHASES else 90
    after_asc_level = int(ASCENSION_PHASES[-1]["at_level"]) if ASCENSION_PHASES else 80
    leveling_after_last_ascension: dict[str, Any] | None = None
    if level_exp:
        block = weapon_exp_block(level_exp, after_asc_level, max_level)
        if block.get("total_exp", 0) > 0:
            leveling_after_last_ascension = {
                "label": f"Montee {after_asc_level} -> {max_level} (apres derniere ascension)",
                **block,
            }
            leveling_mora_total = _accumulate_leveling(block, ore_totals, leveling_mora_total)
    exp_to_max = weapon_exp_block(level_exp, 1, max_level) if level_exp else None

    report: dict[str, Any] = {
        "name": weapon.get("name", ""),
        "id": weapon.get("id", ""),
        "url": weapon.get("url", ""),
        "ascensions": phases_out,
        "totals": totals,
        "total_mora": total_mora,
        "leveling_after_last_ascension": leveling_after_last_ascension,
        "enhancement_ores_total": [
            {"name": n, "count": c} for n, c in sorted(ore_totals.items(), key=lambda x: x[0].lower())
        ],
        "leveling_mora_total": leveling_mora_total,
        "exp_to_level_90": exp_to_max,
    }
    if not level_exp:
        report["enhancement_exp"] = {
            "ore_types": WEAPON_ENHANCEMENT_ORES,
            "mora_per_exp": "1 mora per 10 EXP",
            "note": "Courbe d'EXP absente : regenerez les loadouts (assign) avec weapons_nanoka.json.",
        }
    return report


def build_all_weapon_reports(
    loadouts: list[dict], level_exp_index: dict[str, list[int]] | None = None
) -> list[dict]:
    return sorted(
        [build_weapon_report(w, level_exp_index) for w in loadouts if isinstance(w, dict)],
        key=lambda x: str(x.get("name", "")).lower(),
    )


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Rapport de planification des ascensions armes.")
    p.add_argument("--loadouts", type=Path, default=WEAPON_LOADOUTS_JSON)
    p.add_argument("--weapons", type=Path, default=WEAPONS_JSON, help="JSON bruts (xp_requirements)")
    p.add_argument("--out", type=Path, default=WEAPON_ASCENSION_REPORT_JSON)
    p.add_argument("--weapon", type=str, default="", help="Filtrer par nom d'arme (partiel, insensible à la casse)")
    p.add_argument("--print", dest="show", action="store_true", help="Afficher le rapport dans le terminal")
    return p.parse_args()


def print_weapon_report(report: dict) -> None:
    print(f"\n{'=' * 60}")
    print(f"{report['name']} (id {report['id']})")
    print(f"{'=' * 60}")
    for step in report.get("ascensions") or []:
        print(f"\n  {step['label']} - {step['mora']:,} mora (ascension)")
        leveling = step.get("leveling")
        if leveling:
            print(
                f"    EXP {leveling['from_level']}->{leveling['to_level']}: "
                f"{leveling['total_exp']:,} ({leveling['ore_count']} minerais, "
                f"{leveling['mora_cost']:,} mora XP)"
            )
            for ore in leveling.get("ores") or []:
                print(f"      x{ore['count']:>3}  {ore['name']}")
            if leveling.get("remainder_exp"):
                print(f"      (reste {leveling['remainder_exp']:,} EXP non couvert par les minerais)")
        if not step.get("materials"):
            print("    (aucun materiau d'ascension)")
        else:
            for m in step["materials"]:
                print(f"    x{m['count']:>3}  {m['name']}")
    after = report.get("leveling_after_last_ascension")
    if after:
        print(f"\n  {after['label']}")
        print(
            f"    EXP {after['from_level']}->{after['to_level']}: "
            f"{after['total_exp']:,} ({after['ore_count']} minerais, "
            f"{after['mora_cost']:,} mora XP)"
        )
        for ore in after.get("ores") or []:
            print(f"      x{ore['count']:>3}  {ore['name']}")
        if after.get("remainder_exp"):
            print(f"      (reste {after['remainder_exp']:,} EXP non couvert par les minerais)")
    exp90 = report.get("exp_to_level_90")
    if exp90:
        print(
            f"\n  Total 1->{exp90['to_level']} : {exp90['total_exp']:,} EXP, "
            f"{exp90['ore_count']} minerais, {exp90['mora_cost']:,} mora XP"
        )
        for ore in exp90.get("ores") or []:
            print(f"    x{ore['count']:>3}  {ore['name']}")
    if report.get("enhancement_ores_total"):
        print("\n  Cumul minerais d'EXP (toutes montees, dont 80->90) :")
        for row in report["enhancement_ores_total"]:
            print(f"    x{row['count']:>3}  {row['name']}")
        print(f"  Total mora XP (montees) : {report.get('leveling_mora_total', 0):,}")
    print(f"\n  Total mora (ascensions) : {report.get('total_mora', 0):,}")
    print("  Cumul materiaux d'ascension :")
    for row in report.get("totals") or []:
        print(f"    x{row['count']:>3}  {row['name']}")
    exp = report.get("enhancement_exp") or {}
    if exp.get("note"):
        print(f"\n  Note : {exp['note']}")


def main() -> None:
    ensure_data_dirs()
    args = parse_args()
    loadouts = load_json(args.loadouts) if args.loadouts.is_file() else []
    weapons = load_json(args.weapons) if args.weapons.is_file() else []
    level_exp_index = index_weapon_level_exp(weapons) if weapons else {}
    reports = build_all_weapon_reports(loadouts, level_exp_index)
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
