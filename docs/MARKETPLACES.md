# Marketplaces

Reference data for all five supported marketplaces. Verified April 2026.

```
┌─────────────────┬───────────────┬───────────┬──────────────┐
│  MARKETPLACE    │  SELLER FEE   │ BUYER FEE │  TRADE HOLD  │
├─────────────────┼───────────────┼───────────┼──────────────┤
│  Steam Market   │  15.0%        │   0.0%    │   7 days     │
│  Skinport       │   8.0%        │   0.0%    │   none (P2P) │
│  CSFloat        │   2.0%        │   0.0%    │   none (P2P) │
│  DMarket        │   5.0%        │   2.5%    │   none       │
│  Buff163        │   2.5%        │   0.0%    │   CN only    │
└─────────────────┴───────────────┴───────────┴──────────────┘
```

## Steam Community Market

```
seller fee     15% (5% Steam + 10% game publisher)
buyer fee      0%
trade hold     7 days on purchases
withdrawal     Steam Wallet only, no fiat
api            /market/priceoverview/
risks          aggressive IP bans, ToS bans on automation
```

## Skinport

```
seller fee     8% standard, 6% on items >€1000, 2% private sales
buyer fee      0%
trade hold     none (P2P)
withdrawal     bank transfer (Adyen, EU PSD2)
api            /v1/items returns full catalog in one call
note           lowered seller fee from 12% to 8% in July 2025
```

## CSFloat

```
seller fee     2%
buyer fee      0%
withdrawal     0.5–2.5% scaling with lifetime sales volume
trade hold     none (P2P)
api            /api/v1/listings
note           best for float-specific searches
```

## DMarket

```
seller fee     2–10% depending on item liquidity
buyer fee      2.5%
trade hold     none
withdrawal     crypto, bank
note           US-registered, blockchain-verified
```

## Buff163

```
seller fee     2.5%
buyer fee      0%
trade hold     none (P2P)
access         Chinese users only since June 2023
withdrawal     RMB only, requires Chinese ID
note           largest CS2 inventory globally
```

## Volume tiers

The bot uses `volume_7d` as a liquidity filter:

```
green    ≥ 500 sales / 7d    high liquidity
yellow   100–499 sales / 7d  medium
red      < 100 sales / 7d    low, skip by default
```

## Trade hold timing

```
Steam Market purchase  ──▶  7 days  ──▶  available to sell
Skinport / CSFloat     ──▶  instant ──▶  available to sell
DMarket                ──▶  instant ──▶  available to sell
```

This is why Steam Market is a poor SELL destination for fast arbitrage —
the 7-day hold can erase the spread if prices fall.
