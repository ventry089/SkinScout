from parsers.skinport import normalize_skinport
from parsers.steam_market import _parse_money
from parsers.csfloat import cheapest_csfloat


def test_normalize_skinport_basic():
    raw = [
        {
            "market_hash_name": "AK-47 | Redline (Field-Tested)",
            "min_price": 42.30,
            "median_price": 45.10,
            "quantity": 156,
            "item_page": "https://skinport.com/item/ak-47-redline-field-tested",
        }
    ]
    result = normalize_skinport(raw)
    assert "AK-47 | Redline (Field-Tested)" in result
    item = result["AK-47 | Redline (Field-Tested)"]
    assert item["marketplace"] == "skinport"
    assert item["min_price"] == 42.30


def test_normalize_skinport_filters_null_prices():
    raw = [
        {"market_hash_name": "Item A", "min_price": 10.0, "quantity": 1},
        {"market_hash_name": "Item B", "min_price": None, "quantity": 1},
    ]
    result = normalize_skinport(raw)
    assert "Item A" in result
    assert "Item B" not in result


def test_parse_money_dollars():
    assert _parse_money("$58.00") == 58.0


def test_parse_money_with_thousands_separator():
    assert _parse_money("$1,234.50") == 1234.5


def test_parse_money_none():
    assert _parse_money(None) is None


def test_parse_money_invalid():
    assert _parse_money("not money") is None


def test_cheapest_csfloat_picks_lowest():
    listings = [
        {"id": "a", "price": 5800, "item": {"float_value": 0.15}},
        {"id": "b", "price": 4200, "item": {"float_value": 0.22}},
        {"id": "c", "price": 5100, "item": {"float_value": 0.18}},
    ]
    result = cheapest_csfloat(listings)
    assert result["listing_id"] == "b"
    assert result["min_price"] == 42.0


def test_cheapest_csfloat_empty():
    assert cheapest_csfloat([]) is None
