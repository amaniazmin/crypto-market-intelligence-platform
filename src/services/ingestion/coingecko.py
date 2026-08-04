"""
CoinGecko API client for real-time cryptocurrency data.
"""

import httpx
import asyncio
from typing import List, Dict, Optional
from datetime import datetime
import os
from loguru import logger


class CoinGeckoClient:
    """
    Async client for CoinGecko API.
    """
    
    BASE_URL = "https://api.coingecko.com/api/v3"
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_market_data(
        self, 
        vs_currency: str = "usd",
        per_page: int = 50,
        page: int = 1
    ) -> List[Dict]:
        """
        Get current market data for top cryptocurrencies.
        """
        try:
            url = f"{self.BASE_URL}/coins/markets"
            params = {
                "vs_currency": vs_currency,
                "order": "market_cap_desc",
                "per_page": per_page,
                "page": page,
                "sparkline": "false",
                "price_change_percentage": "24h"
            }
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ Fetched {len(data)} cryptocurrencies")
            return data
            
        except httpx.HTTPStatusError as e:
            logger.error(f"API error: {e.response.status_code}")
            return []
        except Exception as e:
            logger.error(f"Error fetching market data: {str(e)}")
            return []
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()