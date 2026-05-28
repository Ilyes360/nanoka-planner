"""Tests pour exp_books.py."""

from __future__ import annotations

import pytest

from nanoka.exp_books import books_for_exp, exp_block, exp_for_level_range


@pytest.fixture
def sample_level_exp() -> list[int]:
    return [1000] * 89


class TestExpForLevelRange:
    def test_level_1_to_20(self, sample_level_exp: list[int]) -> None:
        assert exp_for_level_range(sample_level_exp, 1, 20) == 19_000

    def test_level_20_to_40(self, sample_level_exp: list[int]) -> None:
        assert exp_for_level_range(sample_level_exp, 20, 40) == 20_000

    def test_invalid_range(self, sample_level_exp: list[int]) -> None:
        assert exp_for_level_range(sample_level_exp, 40, 20) == 0
        assert exp_for_level_range([], 1, 20) == 0


class TestBooksForExp:
    def test_zero(self) -> None:
        assert books_for_exp(0)["book_count"] == 0

    def test_greedy_heroes_wit(self) -> None:
        plan = books_for_exp(45_000)
        assert plan["books"][0] == {
            "name": "Hero's Wit",
            "count": 2,
            "exp_per_book": 20_000,
            "exp_total": 40_000,
        }
        assert plan["book_count"] == 2 + 1  # +1 adventurer
        assert plan["remainder_exp"] == 0

    def test_remainder(self) -> None:
        plan = books_for_exp(23_500)
        assert plan["books"][0]["name"] == "Hero's Wit"
        assert plan["remainder_exp"] == 500
        covered = sum(b["exp_total"] for b in plan["books"])
        assert covered + plan["remainder_exp"] == 23_500


class TestExpBlock:
    def test_includes_range_and_books(self, sample_level_exp: list[int]) -> None:
        block = exp_block(sample_level_exp, 1, 20)
        assert block["from_level"] == 1
        assert block["to_level"] == 20
        assert block["total_exp"] == 19_000
        assert block["book_count"] > 0

