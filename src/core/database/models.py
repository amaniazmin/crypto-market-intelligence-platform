"""
Database models for cryptocurrency data.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Index
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class CryptoPrice(Base):
    """Model for cryptocurrency price data."""
    __tablename__ = 'crypto_prices'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    current_price = Column(Float, nullable=False)
    market_cap = Column(Float)
    total_volume = Column(Float)
    high_24h = Column(Float)
    low_24h = Column(Float)
    price_change_24h = Column(Float)
    price_change_percentage_24h = Column(Float)
    last_updated = Column(DateTime, default=datetime.now, index=True)
    source = Column(String(50), default="coingecko")
    raw_data = Column(JSON)  # Store raw API response
    
    __table_args__ = (
        Index('idx_symbol_time', 'symbol', 'last_updated'),
    )