"""
Data ingestion service for cryptocurrency prices.
"""

from .coingecko import CoinGeckoClient
from ...core.database.connection import SessionLocal
from ...core.database.models import CryptoPrice
from datetime import datetime
from loguru import logger
import asyncio


class DataIngestionService:
    """
    Service for ingesting cryptocurrency data.
    """
    
    def __init__(self):
        self.client = CoinGeckoClient()
        self.is_running = False
    
    async def fetch_and_store(self):
        """
        Fetch market data and store in database.
        """
        try:
            # Fetch data from API
            data = await self.client.get_market_data(per_page=50)
            
            if not data:
                logger.warning("No data received from API")
                return
            
            # Store in database
            db = SessionLocal()
            try:
                for coin in data:
                    price = CryptoPrice(
                        symbol=coin.get('symbol', '').upper(),
                        name=coin.get('name', 'Unknown'),
                        current_price=coin.get('current_price', 0),
                        market_cap=coin.get('market_cap', 0),
                        total_volume=coin.get('total_volume', 0),
                        high_24h=coin.get('high_24h', 0),
                        low_24h=coin.get('low_24h', 0),
                        price_change_24h=coin.get('price_change_24h', 0),
                        price_change_percentage_24h=coin.get('price_change_percentage_24h', 0),
                        last_updated=datetime.now(),
                        source="coingecko",
                        raw_data=coin
                    )
                    db.add(price)
                
                db.commit()
                logger.info(f"✅ Stored {len(data)} prices in database")
                
            except Exception as e:
                db.rollback()
                logger.error(f"Database error: {str(e)}")
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Ingestion failed: {str(e)}")
    
    async def run_continuous(self, interval_seconds: int = 60):
        """
        Run continuous ingestion with specified interval.
        """
        self.is_running = True
        logger.info(f"🚀 Starting continuous ingestion (every {interval_seconds}s)")
        
        while self.is_running:
            try:
                await self.fetch_and_store()
                await asyncio.sleep(interval_seconds)
            except KeyboardInterrupt:
                logger.info("Stopping ingestion...")
                break
            except Exception as e:
                logger.error(f"Error in continuous ingestion: {str(e)}")
                await asyncio.sleep(10)
        
        await self.client.close()
    
    def stop(self):
        """Stop continuous ingestion."""
        self.is_running = False
        logger.info("Stopping ingestion service")