"""Tests pour weapon_exp.py."""

from __future__ import annotations

import pytest

from nanoka.weapon_exp import ores_for_exp, parse_level_exp, weapon_exp_block


@pytest.fixture
def sample_level_exp() -> list[int]:
    return [1000] * 89


class TestParseLevelExp:
    def test_from_list(self) -> None:
        assert parse_level_exp({"level_exp": [100, 200]}) == [100, 200]

    def test_from_xp_requirements(self) -> None:
        assert parse_level_exp({"xp_requirements": {"2": 500, "1": 400}}) == [400, 500]


class TestOresForExp:
    def test_greedy_mystic_ore(self) -> None:
        plan = ores_for_exp(25_000)
        assert plan["ores"][0]["name"] == "Mystic Enhancement Ore"
        assert plan["ores"][0]["count"] == 2
        covered = sum(o["exp_total"] for o in plan["ores"])
        assert covered + plan["remainder_exp"] == 25_000


class TestWeaponExpBlock:
    def test_includes_ores_and_mora(self, sample_level_exp: list[int]) -> None:
        block = weapon_exp_block(sample_level_exp, 1, 20)
        assert block["total_exp"] == 19_000
        assert block["mora_cost"] == 1_900
        assert block["ore_count"] > 0
