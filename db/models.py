from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class PriceSnapshot(Base):
    __tablename__ = "price_snapshots"

    id = Column(Integer, primary_key=True)
    market_hash_name = Column(String, index=True, nullable=False)
    marketplace = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    volume_7d = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class ArbitrageAlert(Base):
    __tablename__ = "arbitrage_alerts"

    id = Column(Integer, primary_key=True)
    market_hash_name = Column(String, index=True)
    buy_market = Column(String)
    buy_price = Column(Float)
    sell_market = Column(String)
    sell_price = Column(Float)
    profit_usd = Column(Float)
    profit_pct = Column(Float)
    volume_7d = Column(Integer)
    notified = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class ItemBlacklist(Base):
    __tablename__ = "blacklist"

    id = Column(Integer, primary_key=True)
    market_hash_name = Column(String, unique=True, nullable=False)
    reason = Column(String)
    added_at = Column(DateTime, default=datetime.utcnow)
