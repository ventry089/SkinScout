# SkinScout

CS2 skin arbitrage scanner. Monitors prices across Steam Market, Skinport, and CSFloat. Calculates real net profit after all marketplace fees. Prints alerts to terminal.

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│   Skinport API   ──┐                                         │
│                    │                                         │
│   Steam Market   ──┼──▶  Spread Calculator  ──▶  Alerts     │
│                    │                                         │
│   CSFloat API    ──┘                                         │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## Marketplace fees (April 2026)

```
┌─────────────────┬───────────────┬───────────┬──────────────┐
│  MARKETPLACE    │  SELLER FEE   │ BUYER FEE │  TRADE HOLD  │
├─────────────────┼───────────────┼───────────┼──────────────┤
│  Steam Market   │  15.0%        │   0.0%    │   7 days     │
│  Skinport       │  8.0%         │   0.0%    │   none (P2P) │
│  CSFloat        │  2.0%         │   0.0%    │   none (P2P) │
│  DMarket        │  5.0%         │   2.5%    │   none       │
│  Buff163        │  2.5%         │   0.0%    │   CN only    │
└─────────────────┴───────────────┴───────────┴──────────────┘
```

- Skinport reduced seller fee from 12% to 8% in July 2025
- Buff163 closed registration for non-Chinese users in June 2023
- CSFloat charges additional 0.5–2.5% withdrawal scaling with volume
- DMarket fee varies 2–10% based on item liquidity

## Project structure

```
SkinScout/
├── arbitrage_scanner.py        entry point
├── live_scan.py                quick demo scanner
├── demo_calculation.py         spread math demo
├── config.py                   fees, thresholds, endpoints
├── conftest.py                 pytest path setup
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
├── core/
│   ├── orchestrator.py         main scan loop
│   └── spread_calculator.py    profit math
│
├── parsers/
│   ├── skinport.py             Skinport API client
│   ├── steam_market.py         Steam priceoverview client
│   └── csfloat.py              CSFloat listings client
│
├── db/
│   ├── models.py               SQLAlchemy ORM
│   └── session.py              SQLite connection
│
├── utils/
│   ├── rate_limiter.py         token-bucket throttler
│   └── proxy_rotator.py        proxy cycling
│
├── tests/
│   ├── test_spread_calculator.py
│   └── test_parsers.py
│
├── backtests/
│   └── historical_analysis.py  reads alerts from DB
│
├── scripts/
│   ├── init_database.py
│   └── blacklist_manager.py
│
└── docs/
    ├── ARCHITECTURE.md
    └── MARKETPLACES.md
```

## Getting started

```bash
git clone https://github.com/yourname/SkinScout.git
cd SkinScout
pip install -r requirements.txt

python demo_calculation.py     # spread math demo
pytest tests/ -v               # run all tests
python arbitrage_scanner.py    # full scanner
```

## How it works

```
   ┌────────────────────────┐
   │  Skinport bulk fetch   │   thousands of items in one request
   └────────────┬───────────┘
                │
                ▼
   ┌────────────────────────┐
   │  Filter candidates     │   $5–$500 range, qty ≥ 5
   │                        │   keep top 200 by liquidity
   └────────────┬───────────┘
                │
                ▼
   ┌────────────────────────┐
   │  Steam priceoverview   │   per-item lookup
   │                        │   3 sec rate limit
   └────────────┬───────────┘
                │
                ▼
   ┌────────────────────────┐
   │  find_arbitrage()      │   fees + safety margin
   │                        │   min profit $3, min ROI 5%
   └────────────┬───────────┘
                │
                ▼
   ┌────────────────────────┐
   │  Print + save to DB    │   alerts table for backtest
   └────────────────────────┘
```

## Why no auto-buy

```
┌──────────────────────────┬─────────────────────────────────┐
│  Steam Mobile Auth       │  every trade requires manual    │
│                          │  confirmation from your phone   │
├──────────────────────────┼─────────────────────────────────┤
│  7-day trade hold        │  bought skins are locked        │
│                          │  price can drop 20–30% in week  │
├──────────────────────────┼─────────────────────────────────┤
│  Steam ToS               │  automated trading is banned    │
│                          │  account bans are permanent     │
└──────────────────────────┴─────────────────────────────────┘
```

The scanner finds opportunities. The user decides whether to buy.

## Stack

```
aiohttp        async http client
SQLAlchemy     ORM + SQLite
loguru         structured logging
pytest         test runner
python-dotenv  env config
```

No ML, no AI inference. Just fee math and API parsing.

## Risks

- 7-day Steam trade hold can erase profit if market drops
- Low-liquidity skins may take months to sell
- Steam aggressively rate-limits and bans scrapers — use proxy rotation
- Buff163 blocks non-Chinese IPs at the network level

## License

MIT
