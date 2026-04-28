import asyncio
import aiohttp
from loguru import logger

from config import SKINPORT_API_BASE, RATE_LIMITS


CS2_APP_ID = 730


async def fetch_skinport_items(session, currency="USD", tradable=True):
    url = f"{SKINPORT_API_BASE}/items"
    params = {
        "app_id": CS2_APP_ID,
        "currency": currency,
        "tradable": str(tradable).lower(),
    }

    await asyncio.sleep(RATE_LIMITS["skinport"])

    try:
        async with session.get(url, params=params, timeout=30) as resp:
            if resp.status == 429:
                logger.warning("skinport rate limit hit, waiting 60s")
                await asyncio.sleep(60)
                return []
            resp.raise_for_status()
            data = await resp.json()
            logger.info(f"skinport: fetched {len(data)} items")
            return data
    except aiohttp.ClientError as e:
        logger.error(f"skinport error: {e}")
        return []


def normalize_skinport(raw):
    return {
        item["market_hash_name"]: {
            "marketplace": "skinport",
            "min_price": item["min_price"],
            "median_price": item.get("median_price"),
            "quantity": item["quantity"],
            "url": item.get("item_page", ""),
        }
        for item in raw
        if item.get("min_price") is not None
    }
