"""
Price endpoints for cryptocurrency data.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from ...core.database.connection import get_db
from ...core.database.models import CryptoPrice
from ...api.routes.auth import get_current_user

router = APIRouter(prefix="/prices", tags=["Prices"])


@router.get("/latest")
async def get_latest_prices(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get the latest prices for top cryptocurrencies.
    Requires authentication.
    """
    # Get the most recent price entry for each symbol
    from sqlalchemy import distinct, func
    
    # Get distinct symbols with their latest timestamp
    subquery = db.query(
        CryptoPrice.symbol,
        func.max(CryptoPrice.last_updated).label('max_updated')
    ).group_by(CryptoPrice.symbol).subquery()
    
    # Get full records for those latest entries
    prices = db.query(CryptoPrice).join(
        subquery,
        (CryptoPrice.symbol == subquery.c.symbol) &
        (CryptoPrice.last_updated == subquery.c.max_updated)
    ).order_by(CryptoPrice.market_cap.desc()).limit(limit).all()
    
    return prices


@router.get("/history/{symbol}")
async def get_price_history(
    symbol: str,
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get historical price data for a specific cryptocurrency.
    Requires authentication.
    """
    cutoff_date = datetime.now() - timedelta(days=days)
    
    prices = db.query(CryptoPrice).filter(
        CryptoPrice.symbol == symbol.upper(),
        CryptoPrice.last_updated >= cutoff_date
    ).order_by(CryptoPrice.last_updated.asc()).all()
    
    if not prices:
        raise HTTPException(status_code=404, detail=f"No data found for symbol: {symbol}")
    
    return prices


@router.get("/top")
async def get_top_performers(
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get top performing cryptocurrencies (24h change).
    Requires authentication.
    """
    # Get latest prices
    subquery = db.query(
        CryptoPrice.symbol,
        func.max(CryptoPrice.last_updated).label('max_updated')
    ).group_by(CryptoPrice.symbol).subquery()
    
    prices = db.query(CryptoPrice).join(
        subquery,
        (CryptoPrice.symbol == subquery.c.symbol) &
        (CryptoPrice.last_updated == subquery.c.max_updated)
    ).order_by(
        CryptoPrice.price_change_percentage_24h.desc()
    ).limit(limit).all()
    
    return prices