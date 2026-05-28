from nanoka.item_icons import resolve_icon_url, static_item_icon_url
from nanoka.report_common import aggregate_totals, slim_material


def test_static_item_icon_url() -> None:
    assert static_item_icon_url(104121).endswith("UI_ItemIcon_104121.webp")


def test_resolve_icon_url_from_name_for_exp_book() -> None:
    url = resolve_icon_url(name="Hero's Wit")
    assert "104003" in url


def test_aggregate_totals_preserves_icon_url() -> None:
    steps = [
        {
            "mora": 100,
            "materials": [
                {"name": "Slime", "count": 2, "item_id": 112002, "icon_url": "https://example.com/a.webp"},
            ],
        },
        {
            "mora": 0,
            "materials": [
                {"name": "Slime", "count": 3, "item_id": 112002, "icon_url": "https://example.com/a.webp"},
            ],
        },
    ]
    totals, mora = aggregate_totals(steps)
    assert mora == 100
    assert len(totals) == 1
    assert totals[0]["count"] == 5
    assert totals[0]["icon_url"] == "https://example.com/a.webp"
    assert totals[0]["item_id"] == 112002


def test_slim_material_fills_icon_from_item_id() -> None:
    row = slim_material(
        {
            "name": "Gem",
            "count": 1,
            "item": {"item_id": 104121, "icon_url": ""},
        }
    )
    assert "104121" in row["icon_url"]
