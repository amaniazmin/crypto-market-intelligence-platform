"""
Script to ingest historical cryptocurrency data.
Run this once to populate your database with history.
"""

import asyncio
import httpx
from datetime import datetime, timedelta
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.database.connection import SessionLocal
from src.core.database.models import CryptoPrice


async def fetch_historical_prices(coin_id: str, days: int = 30):
    """
    Fetch historical price data for a specific coin using market_chart endpoint.
    """
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days,
        "interval": "daily"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                print(f"Error fetching {coin_id}: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error: {str(e)}")
            return None


async def ingest_historical_data():
    """
    Ingest historical data for top cryptocurrencies.
    """
    # CoinGecko IDs (lowercase, hyphenated)
    coins = [
        {"id": "bitcoin", "symbol": "BTC", "name": "Bitcoin"},
        {"id": "ethereum", "symbol": "ETH", "name": "Ethereum"},
        {"id": "binancecoin", "symbol": "BNB", "name": "BNB"},
        {"id": "ripple", "symbol": "XRP", "name": "XRP"},
        {"id": "solana", "symbol": "SOL", "name": "Solana"},
        {"id": "cardano", "symbol": "ADA", "name": "Cardano"},
        {"id": "polkadot", "symbol": "DOT", "name": "Polkadot"},
        {"id": "dogecoin", "symbol": "DOGE", "name": "Dogecoin"},
    ]
    
    print("🔄 Starting historical data ingestion...")
    print(f"📊 Fetching data for: {', '.join([c['symbol'] for c in coins])}")
    print("⏳ This will take about 2-3 minutes...")
    
    db = SessionLocal()
    total_records = 0
    
    try:
        for coin in coins:
            print(f"\n📥 Fetching {coin['symbol']} ({coin['id']})...")
            
            # Fetch 30 days of data
            data = await fetch_historical_prices(coin['id'], days=30)
            
            if not data or 'prices' not in data:
                print(f"⚠️ No data for {coin['symbol']}")
                continue
            
            prices = data['prices']
            print(f"📊 Received {len(prices)} price points")
            
            # Store each historical data point
            record_count = 0
            for price_point in prices:
                timestamp_ms, price = price_point
                # Convert timestamp from ms to datetime
                dt = datetime.fromtimestamp(timestamp_ms / 1000)
                
                # Try to get volume data if available
                volume = 0
                if 'total_volumes' in data and len(data['total_volumes']) > record_count:
                    try:
                        volume = data['total_volumes'][record_count][1]
                    except:
                        pass
                
                # Create a price record
                price_record = CryptoPrice(
                    symbol=coin['symbol'],
                    name=coin['name'],
                    current_price=price,
                    market_cap=0,  # Not available from this endpoint
                    total_volume=volume,
                    high_24h=price,  # Approximation
                    low_24h=price,   # Approximation
                    price_change_24h=0,
                    price_change_percentage_24h=0,
                    last_updated=dt,
                    source="coingecko_historical",
                    raw_data={"timestamp": timestamp_ms, "price": price, "volume": volume}
                )
                db.add(price_record)
                record_count += 1
                total_records += 1
            
            print(f"✅ Stored {record_count} records for {coin['symbol']}")
            
            # Be respectful to the API (rate limiting)
            await asyncio.sleep(2)
        
        db.commit()
        print(f"\n✅ Successfully ingested {total_records} historical records!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Starting historical data ingestion...")
    print("⏳ This may take a minute...")
    asyncio.run(ingest_historical_data())
    print("\n✨ Done! You can now restart the dashboard.")