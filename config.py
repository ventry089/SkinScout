import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class MarketplaceFees:
    name: str
    seller_fee: float
    buyer_fee: float


MARKETS = {
    "steam":    MarketplaceFees("Steam Market",  0.15,  0.00),
    "skinport": MarketplaceFees("Skinport",      0.08,  0.00),
    "csfloat":  MarketplaceFees("CSFloat",       0.02,  0.00),
    "dmarket":  MarketplaceFees("DMarket",       0.05,  0.025),
    "buff163":  MarketplaceFees("Buff163",       0.025, 0.00),
}

MIN_PROFIT_USD       = 3.00
MIN_PROFIT_PERCENT   = 5.0
SAFETY_MARGIN_PCT    = 2.0
MIN_VOLUME_7D        = 50
MAX_ITEM_PRICE_USD   = 500
SCAN_INTERVAL_SEC    = 900

SKINPORT_API_BASE  = "https://api.skinport.com/v1"
CSFLOAT_API_BASE   = "https://csfloat.com/api/v1"
STEAM_MARKET_BASE  = "https://steamcommunity.com/market"

RATE_LIMITS = {
    "steam":    3.0,
    "skinport": 0.5,
    "csfloat":  1.0,
}

TG_BOT_TOKEN  = os.getenv("TG_BOT_TOKEN", "")
TG_ADMIN_ID   = int(os.getenv("TG_ADMIN_ID", "0"))

DB_PATH = "skinscout.db"
LOG_LEVEL = "INFO"
LOG_FILE  = "skinscout.log"
