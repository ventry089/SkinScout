import asyncio
import aiohttp
from loguru import logger

from config import (
    SCAN_INTERVAL_SEC,
    MIN_VOLUME_7D,
    MAX_ITEM_PRICE_USD,
    MARKETS,
)
from parsers.skinport import fetch_skinport_items, normalize_skinport
from parsers.steam_market import fetch_steam_price
from core.spread_calculator import find_arbitrage
from db.session import get_session, init_db
from db.models import ArbitrageAlert


def print_alert(opp):
    print()
    print("=" * 60)
    print(f"  ARBITRAGE: {opp.market_hash_name}")
    print("=" * 60)
    print(f"  Buy on  {MARKETS[opp.buy_market].name:<15} ${opp.buy_price:>7.2f}")
    print(f"  Sell on {MARKETS[opp.sell_market].name:<15} ${opp.sell_proceeds:>7.2f} (net)")
    print(f"  Profit:  ${opp.profit_usd:>7.2f}  ({opp.profit_pct:+.2f}%)")
    print(f"  Volume:  {opp.volume_7d} sales / 7d")
    print("=" * 60)


def save_alert(opp):
    session = get_session()
    record = ArbitrageAlert(
        market_hash_name=opp.market_hash_name,
        buy_market=opp.buy_market,
        buy_price=opp.buy_price,
        sell_market=opp.sell_market,
        sell_price=opp.sell_price_listed,
        profit_usd=opp.profit_usd,
        profit_pct=opp.profit_pct,
        volume_7d=opp.volume_7d,
    )
    session.add(record)
    session.commit()
    session.close()


async def scan_once():
    logger.info("starting scan")

    async with aiohttp.ClientSession() as session:
        skinport_raw = await fetch_skinport_items(session)
        skinport_data = normalize_skinport(skinport_raw)

        candidates = [
            (name, info)
            for name, info in skinport_data.items()
            if info["min_price"] >= 5
            and info["min_price"] <= MAX_ITEM_PRICE_USD
            and info["quantity"] >= 5
        ][:200]

        logger.info(f"checking {len(candidates)} candidates against steam")

        opportunities_found = 0
        for name, skinport_info in candidates:
            steam_price = await fetch_steam_price(session, name)
            if not steam_price:
                continue
            if steam_price["volume"] < MIN_VOLUME_7D:
                continue

            prices = {
                "skinport": skinport_info,
                "steam": steam_price,
            }

            opp = find_arbitrage(
                market_hash_name=name,
                prices=prices,
                volume_7d=steam_price["volume"],
            )

            if opp:
                print_alert(opp)
                save_alert(opp)
                opportunities_found += 1

        logger.info(f"scan done, found {opportunities_found} opportunities")


async def main():
    init_db()
    while True:
        try:
            await scan_once()
        except Exception as e:
            logger.exception(f"scan failed: {e}")
        logger.info(f"sleeping {SCAN_INTERVAL_SEC}s")
        await asyncio.sleep(SCAN_INTERVAL_SEC)


if __name__ == "__main__":
    asyncio.run(main())
