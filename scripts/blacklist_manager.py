import argparse

from db.session import get_session, init_db
from db.models import ItemBlacklist


def add(market_hash_name, reason=""):
    session = get_session()
    existing = session.query(ItemBlacklist).filter_by(
        market_hash_name=market_hash_name
    ).first()
    if existing:
        print(f"already blacklisted: {market_hash_name}")
        session.close()
        return

    item = ItemBlacklist(market_hash_name=market_hash_name, reason=reason)
    session.add(item)
    session.commit()
    print(f"blacklisted: {market_hash_name}")
    session.close()


def remove(market_hash_name):
    session = get_session()
    item = session.query(ItemBlacklist).filter_by(
        market_hash_name=market_hash_name
    ).first()
    if not item:
        print(f"not in blacklist: {market_hash_name}")
        session.close()
        return

    session.delete(item)
    session.commit()
    print(f"removed from blacklist: {market_hash_name}")
    session.close()


def show():
    session = get_session()
    items = session.query(ItemBlacklist).all()
    if not items:
        print("blacklist is empty")
    else:
        for item in items:
            print(f"  {item.market_hash_name} — {item.reason or '(no reason)'}")
    session.close()


if __name__ == "__main__":
    init_db()
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add")
    p_add.add_argument("name")
    p_add.add_argument("--reason", default="")

    p_rm = sub.add_parser("remove")
    p_rm.add_argument("name")

    sub.add_parser("show")

    args = parser.parse_args()

    if args.cmd == "add":
        add(args.name, args.reason)
    elif args.cmd == "remove":
        remove(args.name)
    elif args.cmd == "show":
        show()
