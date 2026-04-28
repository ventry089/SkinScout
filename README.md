# SkinScout

A scanner that finds price differences for CS2 skins across 5 marketplaces. It accounts for every fee on every platform, so when it shows a spread - that spread is real money.

The bot does not buy anything. It only finds opportunities. The user decides what to do with them.

---

## What this is

CS2 skins trade on multiple marketplaces at the same time. The same skin has a different price on each one. Sometimes the difference is enough to cover all the fees and still leave profit.

This is the spread:

```
  Same skin: AK-47 | Redline (Field-Tested)

  Skinport          $42.30
  CSFloat           $43.10
  DMarket           $54.80
  Steam Market      $58.00
  Buff163           $39.50
```

A naive look says "buy on Buff163 for $39.50, sell on Steam for $58 - 47% profit". A real look says "Steam takes 15% from sellers, so you only get $49.30 - and Buff163 only works for Chinese accounts anyway".

The point of this bot is to do the real math automatically.

---

## How it works

```
   Skinport API              gives full catalog in one request
       |
       v
   Filter candidates         only $5-$500 range, qty >= 5
       |                     keep top 200 by liquidity
       v
   Steam Market API          per-item lookup
       |                     3 second rate limit
       v
   spread_calculator         apply all fees, safety margin
       |                     keep only profit > $3 and ROI > 5%
       v
   Print to terminal         + save to SQLite for backtest
```

The bottleneck is Steam. Skinport gives you 47000 skins in one request. Steam wants 200 separate requests with a 3 second cooldown between them - that's 10 minutes per scan.

---

## Marketplace fees - April 2026

```
+------------------+-------------+-----------+--------------+
| MARKETPLACE      | SELLER FEE  | BUYER FEE | TRADE HOLD   |
+------------------+-------------+-----------+--------------+
| Steam Market     | 15.0%       | 0.0%      | 7 days       |
| Skinport         | 8.0%        | 0.0%      | none (P2P)   |
| CSFloat          | 2.0%        | 0.0%      | none (P2P)   |
| DMarket          | 5.0%        | 2.5%      | none         |
| Buff163          | 2.5%        | 0.0%      | CN only      |
+------------------+-------------+-----------+--------------+
```

A few things you need to know about each:

- Steam takes 15% but it splits as 5% Steam + 10% to the game publisher. You can not withdraw to fiat - only Steam Wallet.
- Skinport reduced their fee from 12% to 8% in July 2025. Items above 1000 EUR pay 6%.
- CSFloat charges only 2% but adds a withdrawal fee of 0.5-2.5% depending on your lifetime sales volume.
- DMarket fee is variable - 2-10% based on item liquidity. The 5% in this table is a typical mid-tier value.
- Buff163 closed registration for non-Chinese users in June 2023. You can see prices for reference but you can not actually trade there without a Chinese ID.

---

## Real example

Skinport listing for AK-47 Redline (Field-Tested) at $42.30. Steam Market shows the same skin at $58.00. Naive answer: $15.70 profit. Real math:

```
  BUY ON SKINPORT
    listed:                    $42.30
    + buyer fee (0%):           +0.00
    total cost:                $42.30

  SELL ON STEAM
    listed:                    $58.00
    - seller fee (15%):         -8.70
    proceeds:                  $49.30
    - safety margin (2%):       -0.99
    net proceeds:              $48.31

  PROFIT: $48.31 - $42.30 = $6.01 (+14.21%)
```

Steam quietly takes $8.70 from your sale. Plus a 2% safety margin for price slippage during the 7-day trade hold. The actual profit is $6 not $15.

This is why most arbitrage spreadsheets you see online are wrong. They forget the seller fee.

---

## Why no auto-buy

This bot does not buy anything automatically. There are 3 reasons.

1. **Steam Mobile Authenticator.** Every Steam trade requires you to confirm it on your phone within a minute. Bots can bypass this with steam-totp, but Valve actively bans accounts that do this.

2. **7-day trade hold.** Anything you buy on Steam is locked for 7 days before you can sell it. Skin prices can drop 20-30% in a week, especially around CS2 updates. Your $6 profit becomes a $20 loss.

3. **Steam ToS.** Automated trading is banned in plain text in their terms of service. Account bans are permanent and your inventory becomes inaccessible.

So the bot scans, finds spreads, and prints them. The human looks at the spread, checks the volume, decides if the 7-day hold is worth it, and trades manually.

---

## Project structure

```
SkinScout/
|
|-- arbitrage_scanner.py     - main entry point, runs the scanner forever
|-- live_scan.py             - quick one-shot scan demo
|-- demo_calculation.py      - standalone demo of the spread math
|-- config.py                - all fees, thresholds, endpoints in one place
|-- conftest.py              - pytest path setup
|-- requirements.txt
|-- README.md
|-- .env.example
|-- .gitignore
|
|-- core/
|   |-- orchestrator.py      - main async scan loop
|   `-- spread_calculator.py - profit math after all fees
|
|-- parsers/
|   |-- skinport.py          - Skinport API client
|   |-- steam_market.py      - Steam priceoverview client
|   `-- csfloat.py           - CSFloat listings client
|
|-- db/
|   |-- models.py            - SQLAlchemy ORM tables
|   `-- session.py           - SQLite connection
|
|-- utils/
|   |-- rate_limiter.py      - throttle requests per endpoint
|   `-- proxy_rotator.py     - cycle through proxies
|
|-- tests/
|   |-- test_spread_calculator.py
|   `-- test_parsers.py
|
|-- backtests/
|   `-- historical_analysis.py - read alerts from DB, show stats
|
|-- scripts/
|   |-- init_database.py     - create SQLite tables
|   `-- blacklist_manager.py - exclude bad skins from scan
|
`-- docs/
    |-- ARCHITECTURE.md
    `-- MARKETPLACES.md
```

---

## What each part does

### config.py

All the constants live here. Every fee, every endpoint, every threshold.

```python
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
```

If Skinport drops their fee again, you change one line here and everything else updates automatically.

### parsers/

One file per marketplace. Each parser is async, has its own rate limiter, and returns prices in a normalized format. So the rest of the code does not care which marketplace the data came from.

Skinport is special - it returns the entire catalog in one call. Other marketplaces require per-item requests.

### core/spread_calculator.py

The heart of the project. Takes prices from N marketplaces, tries every buy-sell combination, applies all fees, returns the best opportunity if any clears the profit threshold.

```python
def find_arbitrage(market_hash_name, prices, volume_7d=0):
    ...
    for buy_mkt, buy_listed in min_prices.items():
        for sell_mkt, sell_listed in min_prices.items():
            if buy_mkt == sell_mkt:
                continue

            buy_total = calculate_buy_cost(buy_listed, buy_mkt)
            sell_net = calculate_sell_proceeds(sell_listed, sell_mkt)
            sell_net *= (1 - SAFETY_MARGIN_PCT / 100)

            profit = sell_net - buy_total
            ...
```

If you understand this function, you understand the whole project.

### core/orchestrator.py

The main loop. Pulls prices, sends them to the spread calculator, prints alerts, saves them to SQLite, sleeps 15 minutes, repeats.

### db/

SQLite is enough. The schema has 3 tables:

- `price_snapshots` - history of prices per skin per marketplace
- `arbitrage_alerts` - every spread the bot found
- `blacklist` - skins to skip (rugpulls, low liquidity, whatever)

After a week of running, the alerts table has enough data for a backtest.

### backtests/historical_analysis.py

Reads the alerts table and shows what the bot would have found over the past N days. Useful to tune thresholds.

### tests/

17 unit tests. Run with `pytest tests/`. They check the spread math against known cases - if Steam takes 15% from $100 you should get $85, etc. If you change fees in config.py and forget to update the tests, they will fail.

---

## Running it

```
git clone https://github.com/ventry089/SkinScout.git
cd SkinScout
pip install -r requirements.txt
```

Try the demo first - no API calls, no database, just the math:

```
python demo_calculation.py
```

You should see 3 worked examples of spread calculation.

Run the tests:

```
pytest tests/ -v
```

Should say "17 passed".

Initialize the database:

```
python scripts/init_database.py
```

Run the full scanner (this will hit live APIs):

```
python arbitrage_scanner.py
```

It will fetch Skinport, then check 200 candidates against Steam (slow because of rate limits), then print whatever spreads it finds, then sleep for 15 minutes.

---

## Risks you should know about

This is not financial advice and trading skins is not risk-free.

- **7-day trade hold** can erase your profit if the market drops. CS2 has had multiple 30%+ crashes after major updates.
- **Liquidity matters.** A skin can have a $20 spread but if it sells once a month you might be holding it for 60 days while the price moves.
- **Steam IP bans.** If you scrape too fast they ban your IP for hours or days. Use proxy rotation in production.
- **Skinport requires a Cloudflare bypass** for unauthenticated access. Real production use requires either an API key from them or a service like CSGOSKINS.GG.
- **Buff163 is unreachable** without a Chinese phone number and ID since 2023.
- **Currency conversion** can eat profit too. Skinport defaults to EUR, Steam to your account currency. The bot uses USD throughout.

---

## What I would build next

This is a working MVP. To turn it into something you actually trade with:

- Add a real Steam Market client with proxy rotation and 429 handling
- Add CSGOSKINS.GG aggregator to bypass Cloudflare and include Buff163 prices
- Add float-aware pricing (a 0.07 float AK is worth 3-5x the same skin at 0.15)
- Add a notification layer beyond terminal - Discord webhook, Telegram, push notifications
- Add a backtester that simulates buying every signal and tracks actual P&L
- Add Kelly criterion for position sizing
- Add a portfolio dashboard

If you fork this and add any of those, send me the link.

---

## Stack

```
Python 3.11+
aiohttp        - async HTTP
SQLAlchemy     - ORM for SQLite
loguru         - logging
pytest         - testing
python-dotenv  - .env config
```

No machine learning. No AI inference. Just fee math, async HTTP, and SQLite.

---

## License

MIT - do whatever you want with it.

---

## Why I built this

I wanted to know if CS2 skin arbitrage is actually profitable in 2026 - or if the spreads people post on Reddit are just selection bias from people who got lucky once.

The honest answer after building this: spreads exist, they are real, the math works. But the 7-day Steam trade hold and the 15% Steam seller fee eat most of the obvious opportunities. The remaining ones require either fast manual execution or access to Buff163 (which is gated by nationality).

Most real arbitrage profit in 2026 is between Skinport-CSFloat-DMarket - all P2P, no trade hold. The Steam side of the trade is where retail traders lose because they forget about the fee.

This bot is the answer to "would automated price comparison be useful". Yes - especially if you scan every 15 minutes and react fast.
