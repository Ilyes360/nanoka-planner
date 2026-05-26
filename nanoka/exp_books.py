"""Calcul des livres d'experience requis a partir du tableau level_exp."""

from __future__ import annotations

from typing import TypedDict


class ExpBookDef(TypedDict):
    name: str
    exp: int


# Valeurs standard Genshin Impact
EXP_BOOKS: list[ExpBookDef] = [
    {"name": "Hero's Wit", "exp": 20_000},
    {"name": "Adventurer's Experience", "exp": 5_000},
    {"name": "Wanderer's Advice", "exp": 1_000},
]


def exp_for_level_range(level_exp: list[int], from_level: int, to_level: int) -> int:
    """EXP cumulee pour passer de from_level a to_level (ex. 1->20, 20->40)."""
    if not level_exp or from_level >= to_level or from_level < 1:
        return 0
    start = from_level - 1
    end = to_level - 1
    if start >= len(level_exp):
        return 0
    return int(sum(level_exp[start:end]))


def books_for_exp(total_exp: int) -> dict:
    """Repartit l'EXP en livres (glouton, du plus grand au plus petit)."""
    if total_exp <= 0:
        return {
            "total_exp": 0,
            "books": [],
            "book_count": 0,
            "remainder_exp": 0,
        }
    remaining = total_exp
    books_out: list[dict] = []
    book_count = 0
    for book in EXP_BOOKS:
        count = remaining // book["exp"]
        if count:
            books_out.append(
                {
                    "name": book["name"],
                    "count": count,
                    "exp_per_book": book["exp"],
                    "exp_total": count * book["exp"],
                }
            )
            book_count += count
            remaining -= count * book["exp"]
    return {
        "total_exp": total_exp,
        "books": books_out,
        "book_count": book_count,
        "remainder_exp": remaining,
    }


def exp_block(level_exp: list[int], from_level: int, to_level: int) -> dict:
    total = exp_for_level_range(level_exp, from_level, to_level)
    plan = books_for_exp(total)
    return {
        "from_level": from_level,
        "to_level": to_level,
        **plan,
    }
