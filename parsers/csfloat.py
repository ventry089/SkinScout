import asyncio
import aiohttp
from loguru import logger

from config import CSFLOAT_API_BASE, RATE_LIMITS


async def fetch_csfloat_listings(session, market_hash_name, limit=50):
    url = f"{CSFLOAT_API_BASE}/listings"
    params = {
        "market_hash_name": market_hash_name,
        "limit": limit,
        "sort_by": "lowest_price",
    }

    await asyncio.sleep(RATE_LIMITS["csfloat"])

    try:
        async with session.get(url, params=params, timeout=20) as resp:
            if resp.status == 429:
                logger.warning("csfloat rate limit hit")
                await asyncio.sleep(30)
                return []
            resp.raise_for_status()
            data = await resp.json()
            return data.get("data", [])
    except aiohttp.ClientError as e:
        logger.error(f"csfloat error: {e}")
        return []


def cheapest_csfloat(listings):
    if not listings:
        return None
    cheapest = min(listings, key=lambda l: l["price"])
    return {
        "marketplace": "csfloat",
        "min_price": cheapest["price"] / 100,
        "float_value": cheapest.get("item", {}).get("float_value"),
        "listing_id": cheapest.get("id"),
    }
