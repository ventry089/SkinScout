import pytest

from core.spread_calculator import (
    find_arbitrage,
    calculate_buy_cost,
    calculate_sell_proceeds,
)


def test_steam_seller_fee():
    proceeds = calculate_sell_proceeds(100, "steam")
    assert proceeds == 85.0


def test_skinport_seller_fee():
    proceeds = calculate_sell_proceeds(100, "skinport")
    assert proceeds == 92.0


def test_csfloat_seller_fee():
    proceeds = calculate_sell_proceeds(100, "csfloat")
    assert proceeds == 98.0


def test_dmarket_buyer_fee():
    cost = calculate_buy_cost(100, "dmarket")
    assert cost == pytest.approx(102.5)


def test_no_arbitrage_when_prices_equal():
    prices = {
        "steam": {"min_price": 50.0},
        "skinport": {"min_price": 50.0},
    }
    result = find_arbitrage("AK-47 | Redline (FT)", prices, volume_7d=500)
    assert result is None


def test_arbitrage_skinport_to_steam():
    prices = {
        "skinport": {"min_price": 42.30},
        "steam": {"min_price": 58.00},
    }
    result = find_arbitrage("AK-47 | Redline (FT)", prices, volume_7d=1000)
    assert result is not None
    assert result.buy_market == "skinport"
    assert result.sell_market == "steam"
    assert result.profit_usd > 0


def test_min_profit_threshold():
    prices = {
        "skinport": {"min_price": 10.0},
        "steam": {"min_price": 11.0},
    }
    result = find_arbitrage("Random | Skin (FT)", prices, volume_7d=500)
    assert result is None


def test_buy_cost_no_buyer_fee():
    cost = calculate_buy_cost(100, "skinport")
    assert cost == 100.0


def test_csfloat_to_skinport_arbitrage():
    prices = {
        "csfloat": {"min_price": 100.00},
        "skinport": {"min_price": 120.00},
    }
    result = find_arbitrage("AK-47 | Redline (FT)", prices, volume_7d=300)
    assert result is not None
    assert result.profit_usd > 0
