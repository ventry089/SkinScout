FEES = {
    "Steam Market":     {"seller": 0.15,  "buyer": 0.00},
    "Skinport":         {"seller": 0.08,  "buyer": 0.00},
    "CSFloat":          {"seller": 0.02,  "buyer": 0.00},
    "DMarket":          {"seller": 0.05,  "buyer": 0.025},
    "Buff163":          {"seller": 0.025, "buyer": 0.00},
}


def buy_total(listed_price, market):
    return listed_price * (1 + FEES[market]["buyer"])


def sell_proceeds(listed_price, market):
    return listed_price * (1 - FEES[market]["seller"])


def calculate_spread(buy_market, buy_price, sell_market, sell_price):
    cost = buy_total(buy_price, buy_market)
    proceeds = sell_proceeds(sell_price, sell_market)
    profit = proceeds - cost
    roi = (profit / cost) * 100 if cost > 0 else 0

    print(f"\n{'='*60}")
    print(f"  AK-47 | Redline (Field-Tested)")
    print(f"{'='*60}")
    print(f"  Buy:      {buy_market:<15} listed ${buy_price:>6.2f}")
    print(f"            buyer fee {FEES[buy_market]['buyer']*100:>4.1f}%")
    print(f"            total cost: ${cost:>6.2f}")
    print()
    print(f"  Sell:     {sell_market:<15} listed ${sell_price:>6.2f}")
    print(f"            seller fee {FEES[sell_market]['seller']*100:>4.1f}%")
    print(f"            proceeds:   ${proceeds:>6.2f}")
    print()
    print(f"  PROFIT:   ${profit:>6.2f} ({roi:+.2f}%)")
    print(f"{'='*60}")
    return profit, roi


if __name__ == "__main__":
    print("\n>>> Skinport -> Steam Market")
    calculate_spread("Skinport", 42.30, "Steam Market", 58.00)

    print("\n>>> CSFloat -> Skinport")
    calculate_spread("CSFloat", 41.00, "Skinport", 47.50)

    print("\n>>> Steam -> Steam (counter-example)")
    calculate_spread("Steam Market", 50.00, "Steam Market", 50.00)
