from dataclasses import dataclass

from config import (
    MARKETS,
    MIN_PROFIT_USD,
    MIN_PROFIT_PERCENT,
    SAFETY_MARGIN_PCT,
)


@dataclass
class ArbitrageOpportunity:
    market_hash_name: str
    buy_market: str
    buy_price: float
    sell_market: str
    sell_price_listed: float
    sell_proceeds: float
    profit_usd: float
    profit_pct: float
    volume_7d: int


def calculate_buy_cost(price, market):
    fee = MARKETS[market].buyer_fee
    return price * (1 + fee)


def calculate_sell_proceeds(price, market):
    fee = MARKETS[market].seller_fee
    return price * (1 - fee)


def find_arbitrage(market_hash_name, prices, volume_7d=0):
    min_prices = {}
    for mkt, data in prices.items():
        price = data.get("min_price") or data.get("lowest_price")
        if price and price > 0:
            min_prices[mkt] = price

    if len(min_prices) < 2:
        return None

    best = None

    for buy_mkt, buy_listed in min_prices.items():
        for sell_mkt, sell_listed in min_prices.items():
            if buy_mkt == sell_mkt:
                continue

            buy_total = calculate_buy_cost(buy_listed, buy_mkt)
            sell_net = calculate_sell_proceeds(sell_listed, sell_mkt)
            sell_net *= (1 - SAFETY_MARGIN_PCT / 100)

            profit = sell_net - buy_total
            if buy_total <= 0:
                continue
            profit_pct = (profit / buy_total) * 100

            if profit < MIN_PROFIT_USD:
                continue
            if profit_pct < MIN_PROFIT_PERCENT:
                continue

            if best is None or profit > best.profit_usd:
                best = ArbitrageOpportunity(
                    market_hash_name=market_hash_name,
                    buy_market=buy_mkt,
                    buy_price=round(buy_total, 2),
                    sell_market=sell_mkt,
                    sell_price_listed=round(sell_listed, 2),
                    sell_proceeds=round(sell_net, 2),
                    profit_usd=round(profit, 2),
                    profit_pct=round(profit_pct, 2),
                    volume_7d=volume_7d,
                )

    return best
