# Architecture

## Data flow

```
┌──────────────────────┐
│   Skinport API       │   bulk endpoint
│   /v1/items          │   tens of thousands of items in one call
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   Filter candidates  │   $5–$500, qty ≥ 5
│                      │   top 200 by liquidity
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   Steam Market API   │   per-item lookup
│   /priceoverview/    │   3 sec rate limit
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   spread_calculator  │   fees + safety margin
│   find_arbitrage()   │   min profit $3, min ROI 5%
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   SQLite database    │   price_snapshots
│                      │   arbitrage_alerts
└──────────────────────┘
```

## Modules

```
parsers/        async HTTP clients per marketplace
core/           main scan loop and profit math
db/             SQLAlchemy models and session
utils/          rate limiter, proxy rotator
backtests/      analysis from stored alerts
scripts/        CLI helpers
```

## Why bulk endpoint matters

Skinport returns the entire CS2 catalog in a single request.

Steam Market does not — each skin requires a separate `/priceoverview/` call with a 3-second cooldown.

This is the bottleneck:

```
200 candidates × 3 seconds = 10 minutes per scan
```

## Why SQLite

```
zero setup           file-based, no server
single-writer ok     arbitrage logging is sequential
fast queries         backtests run in ms on 100K+ rows
easy inspection      sqlite3 skinscout.db
```

For multi-process production, swap to PostgreSQL. SQLAlchemy makes it a one-line change.

## Database schema

```
price_snapshots
├── id
├── market_hash_name
├── marketplace
├── price
├── volume_7d
└── timestamp

arbitrage_alerts
├── id
├── market_hash_name
├── buy_market
├── buy_price
├── sell_market
├── sell_price
├── profit_usd
├── profit_pct
├── volume_7d
├── notified
└── timestamp

blacklist
├── id
├── market_hash_name
├── reason
└── added_at
```

## Rate limiting strategy

```
Steam Market    3.0 sec between calls    ban-prone
Skinport        0.5 sec between calls    8 req / 5 min limit
CSFloat         1.0 sec between calls    60 req / min limit
```

If a 429 is received, the parser sleeps and retries with backoff.
