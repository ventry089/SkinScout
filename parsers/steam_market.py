import asyncio
import aiohttp
from urllib.parse import quote
from loguru import logger

from config import STEAM_MARKET_BASE, RATE_LIMITS


USD_CODE = 1


async def fetch_steam_price(session, market_hash_name):
    encoded_name = quote(market_hash_name)
    url = (
        f"{STEAM_MARKET_BASE}/priceoverview/"
        f"?appid=730&currency={USD_CODE}&market_hash_name={encoded_name}"
    )

    await asyncio.sleep(RATE_LIMITS["steam"])

    try:
        async with session.get(url, timeout=15) as resp:
            if resp.status == 429:
                logger.warning(f"steam rate limit on {market_hash_name}, sleeping 5min")
                await asyncio.sleep(300)
                return None
            if resp.status != 200:
                return None

            data = await resp.json()
            if not data.get("success"):
                return None

            return {
                "lowest_price": _parse_money(data.get("lowest_price")),
                "median_price": _parse_money(data.get("median_price")),
                "volume": int(data.get("volume", "0").replace(",", "") or 0),
            }
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        logger.error(f"steam error: {e}")
        return None


def _parse_money(s):
    if not s:
        return None
    cleaned = s.replace("$", "").replace("€", "").replace(",", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return None
