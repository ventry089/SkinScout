import argparse
from datetime import datetime, timedelta

from db.session import get_session, init_db
from db.models import ArbitrageAlert


def run_backtest(days=30):
    init_db()
    session = get_session()
    cutoff = datetime.utcnow() - timedelta(days=days)

    alerts = session.query(ArbitrageAlert).filter(
        ArbitrageAlert.timestamp >= cutoff
    ).all()

    total_signals = len(alerts)
    total_potential_profit = sum(a.profit_usd or 0 for a in alerts)
    avg = total_potential_profit / max(total_signals, 1)

    print(f"PERIOD: last {days} days")
    print(f"{'=' * 50}")
    print(f"Total signals:         {total_signals}")
    print(f"Total profit:          ${total_potential_profit:,.2f}")
    print(f"Average per signal:    ${avg:,.2f}")
    print()

    by_route = {}
    for alert in alerts:
        key = f"{alert.buy_market} -> {alert.sell_market}"
        by_route.setdefault(key, []).append(alert.profit_usd or 0)

    if by_route:
        print("Breakdown by route:")
        sorted_routes = sorted(by_route.items(), key=lambda x: -sum(x[1]))
        for route, profits in sorted_routes:
            print(f"  {route}: {len(profits)} signals, ${sum(profits):,.2f}")
    else:
        print("No data yet. Run the scanner for a few days to populate the database.")

    session.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=30)
    args = parser.parse_args()
    run_backtest(args.days)
