import asyncio
import aiohttp
import sys
from datetime import datetime

sys.path.insert(0, ".")

from config import MARKETS, MIN_PROFIT_USD, MIN_PROFIT_PERCENT, SAFETY_MARGIN_PCT
from core.spread_calculator import find_arbitrage


STEAM_REFERENCE_PRICES = {
    "AK-47 | Redline (Field-Tested)":           58.00,
    "AWP | Asiimov (Field-Tested)":             92.00,
    "M4A4 | Asiimov (Field-Tested)":            68.00,
    "AK-47 | Vulcan (Minimal Wear)":            168.00,
    "Desert Eagle | Blaze (Factory New)":       720.00,
    "USP-S | Kill Confirmed (Field-Tested)":    86.00,
    "AWP | Hyper Beast (Field-Tested)":         42.00,
    "M4A1-S | Hyper Beast (Field-Tested)":      38.00,
    "Glock-18 | Fade (Factory New)":            580.00,
    "AK-47 | Asiimov (Field-Tested)":           62.00,
    "AWP | Neo-Noir (Field-Tested)":            58.00,
    "M4A4 | Howl (Minimal Wear)":               2150.00,
    "Karambit | Doppler (Factory New)":         1080.00,
    "Bayonet | Tiger Tooth (Factory New)":      912.00,
    "AWP | Dragon Lore (Battle-Scarred)":       2780.00,
    "AK-47 | Fire Serpent (Field-Tested)":      1850.00,
    "StatTrak™ AK-47 | Redline (Field-Tested)": 195.00,
    "AWP | Lightning Strike (Factory New)":     520.00,
    "M4A1-S | Knight (Factory New)":            980.00,
    "Glock-18 | Water Elemental (Field-Tested)": 22.00,
}


def print_alert(opp, idx):
    print()
    print("=" * 64)
    print(f"  [{idx}] ARBITRAGE FOUND")
    print("=" * 64)
    print(f"  Item:    {opp.market_hash_name}")
    print(f"  Buy on:  {MARKETS[opp.buy_market].name:<14} ${opp.buy_price:>8.2f}")
    print(f"  Sell on: {MARKETS[opp.sell_market].name:<14} ${opp.sell_proceeds:>8.2f}  net")
    print(f"  Profit:  ${opp.profit_usd:>8.2f}  ({opp.profit_pct:+.2f}%)")
    print(f"  Volume:  {opp.volume_7d} sales / 7d")
    print("=" * 64)


async def fetch_skinport_price(session, market_hash_name):
    url = "https://api.skinport.com/v1/items"
    params = {"app_id": 730, "currency": "USD", "tradable": "true"}

    try:
        async with session.get(url, params=params, timeout=30) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            for item in data:
                if item.get("market_hash_name") == market_hash_name:
                    return {
                        "min_price": item.get("min_price"),
                        "quantity": item.get("quantity", 0),
                    }
            return None
    except Exception:
        return None


async def main():
    started = datetime.now()
    print()
    print("=" * 64)
    print(f"  SKINSCOUT SCANNER — started {started.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 64)
    print(f"  Sources: Skinport (live) + Steam Market reference prices")
    print(f"  Min profit: ${MIN_PROFIT_USD}  |  Min ROI: {MIN_PROFIT_PERCENT}%")
    print(f"  Safety margin: {SAFETY_MARGIN_PCT}%")
    print("=" * 64)

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] fetching Skinport catalog...")

    async with aiohttp.ClientSession() as session:
        url = "https://api.skinport.com/v1/items"
        params = {"app_id": 730, "currency": "USD", "tradable": "true"}

        async with session.get(url, params=params, timeout=30) as resp:
            if resp.status != 200:
                print(f"[ERROR] Skinport returned {resp.status}")
                return
            all_items = await resp.json()

        print(f"[{datetime.now().strftime('%H:%M:%S')}] received {len(all_items)} items from Skinport")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] checking {len(STEAM_REFERENCE_PRICES)} target skins against Steam prices...")

        skinport_lookup = {item["market_hash_name"]: item for item in all_items}

        opportunities = []
        for skin_name, steam_price in STEAM_REFERENCE_PRICES.items():
            skinport_item = skinport_lookup.get(skin_name)
            if not skinport_item or not skinport_item.get("min_price"):
                continue

            prices = {
                "skinport": {"min_price": skinport_item["min_price"]},
                "steam": {"min_price": steam_price},
            }

            opp = find_arbitrage(
                market_hash_name=skin_name,
                prices=prices,
                volume_7d=skinport_item.get("quantity", 0) * 8,
            )

            if opp:
                opportunities.append(opp)

        print(f"[{datetime.now().strftime('%H:%M:%S')}] scan complete\n")

        if opportunities:
            for i, opp in enumerate(opportunities, 1):
                print_alert(opp, i)

            print()
            print("=" * 64)
            print(f"  SUMMARY")
            print("=" * 64)
            total_profit = sum(o.profit_usd for o in opportunities)
            avg_pct = sum(o.profit_pct for o in opportunities) / len(opportunities)
            print(f"  Opportunities found:  {len(opportunities)}")
            print(f"  Total profit:         ${total_profit:.2f}")
            print(f"  Average ROI:          {avg_pct:.2f}%")
            print("=" * 64)
        else:
            print("No arbitrage opportunities right now.")
            print("Try again in 15 minutes — prices fluctuate.")


if __name__ == "__main__":
    asyncio.run(main())
