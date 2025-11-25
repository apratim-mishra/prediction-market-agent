"""Enhanced Price Oracle with Multiple API Support."""
import asyncio
from datetime import datetime
from enum import Enum
from typing import Any, Optional

import aiohttp

from config import config


class PriceSource(Enum):
    """Available price data sources."""
    ALPHA_VANTAGE = "alpha_vantage"
    COINGECKO = "coingecko"
    COINBASE = "coinbase"
    POLYGON = "polygon"


class PriceOracle:
    """Multi-source price oracle for stocks and crypto."""
    
    ENDPOINTS = {
        PriceSource.ALPHA_VANTAGE: "https://www.alphavantage.co/query",
        PriceSource.COINGECKO: "https://api.coingecko.com/api/v3",
        PriceSource.COINBASE: "https://api.coinbase.com/v2",
        PriceSource.POLYGON: "https://api.polygon.io",
    }
    
    CRYPTO_MAPPINGS = {
        "BTC": {"coingecko": "bitcoin", "coinbase": "BTC-USD"},
        "ETH": {"coingecko": "ethereum", "coinbase": "ETH-USD"},
        "SOL": {"coingecko": "solana", "coinbase": "SOL-USD"},
        "AVAX": {"coingecko": "avalanche-2", "coinbase": "AVAX-USD"},
        "MATIC": {"coingecko": "matic-network", "coinbase": "MATIC-USD"},
    }
    
    def __init__(self):
        self.alpha_vantage_key = config.alpha_vantage_api_key
        self.coingecko_key = config.coingecko_api_key
        self.polygon_key = config.polygon_api_key
    
    async def get_price(self, symbol: str) -> float:
        """Get price for any symbol (stock or crypto)."""
        try:
            if symbol.upper() in self.CRYPTO_MAPPINGS:
                result = await self.get_crypto_price(symbol)
            else:
                result = await self.get_stock_price(symbol)
            return result["price"]
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
            return 100.0  # Fallback for testing
    
    async def get_stock_price(self, symbol: str) -> dict[str, Any]:
        """Get stock price from Alpha Vantage or Polygon."""
        if self.alpha_vantage_key:
            return await self._fetch_alpha_vantage(symbol)
        if self.polygon_key:
            return await self._fetch_polygon(symbol, "stocks")
        raise ValueError(
            "No stock API key configured. "
            "Add ALPHA_VANTAGE_API_KEY or POLYGON_API_KEY to .env"
        )
    
    async def get_crypto_price(self, symbol: str) -> dict[str, Any]:
        """Get crypto price from available sources."""
        symbol = symbol.upper()
        if symbol not in self.CRYPTO_MAPPINGS:
            raise ValueError(f"Unknown crypto symbol: {symbol}")
        
        if self.coingecko_key:
            return await self._fetch_coingecko(symbol)
        return await self._fetch_coinbase(symbol)
    
    async def _fetch_alpha_vantage(self, symbol: str) -> dict[str, Any]:
        """Fetch stock price from Alpha Vantage."""
        async with aiohttp.ClientSession() as session:
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": self.alpha_vantage_key,
            }
            async with session.get(
                self.ENDPOINTS[PriceSource.ALPHA_VANTAGE], params=params
            ) as response:
                data = await response.json()
                
                if "Global Quote" not in data:
                    raise ValueError(f"No data found for {symbol}")
                
                quote = data["Global Quote"]
                return {
                    "symbol": symbol,
                    "price": float(quote["05. price"]),
                    "change": float(quote["09. change"]),
                    "change_percent": quote["10. change percent"],
                    "timestamp": datetime.now().isoformat(),
                    "source": "alpha_vantage",
                }
    
    async def _fetch_coingecko(self, symbol: str) -> dict[str, Any]:
        """Fetch crypto price from CoinGecko."""
        gecko_id = self.CRYPTO_MAPPINGS[symbol]["coingecko"]
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.ENDPOINTS[PriceSource.COINGECKO]}/simple/price"
            params = {
                "ids": gecko_id,
                "vs_currencies": "usd",
                "include_24hr_change": "true",
            }
            headers = {}
            if self.coingecko_key:
                headers["x-cg-demo-api-key"] = self.coingecko_key
            
            async with session.get(url, params=params, headers=headers) as response:
                data = await response.json()
                
                if gecko_id not in data:
                    raise ValueError(f"No data found for {symbol}")
                
                return {
                    "symbol": symbol,
                    "price": data[gecko_id]["usd"],
                    "change_24h": data[gecko_id].get("usd_24h_change", 0),
                    "timestamp": datetime.now().isoformat(),
                    "source": "coingecko",
                }
    
    async def _fetch_coinbase(self, symbol: str) -> dict[str, Any]:
        """Fetch crypto price from Coinbase (no API key needed)."""
        async with aiohttp.ClientSession() as session:
            url = f"{self.ENDPOINTS[PriceSource.COINBASE]}/exchange-rates"
            params = {"currency": symbol}
            
            async with session.get(url, params=params) as response:
                data = await response.json()
                
                if "data" not in data or "rates" not in data["data"]:
                    raise ValueError(f"No data found for {symbol}")
                
                return {
                    "symbol": symbol,
                    "price": float(data["data"]["rates"]["USD"]),
                    "timestamp": datetime.now().isoformat(),
                    "source": "coinbase",
                }
    
    async def _fetch_polygon(self, symbol: str, asset_type: str) -> dict[str, Any]:
        """Fetch price from Polygon.io."""
        async with aiohttp.ClientSession() as session:
            if asset_type == "stocks":
                url = f"{self.ENDPOINTS[PriceSource.POLYGON]}/v2/aggs/ticker/{symbol}/prev"
            else:
                url = f"{self.ENDPOINTS[PriceSource.POLYGON]}/v2/aggs/ticker/X:{symbol}USD/prev"
            
            params = {"apiKey": self.polygon_key}
            
            async with session.get(url, params=params) as response:
                data = await response.json()
                
                if "results" not in data or not data["results"]:
                    raise ValueError(f"No data found for {symbol}")
                
                result = data["results"][0]
                return {
                    "symbol": symbol,
                    "price": result["c"],
                    "timestamp": datetime.now().isoformat(),
                    "source": "polygon",
                }
    
    async def resolve_expired_markets(
        self,
        contract_interface,
        market_ids: list[int]
    ) -> None:
        """Resolve expired markets with actual prices."""
        for market_id in market_ids:
            try:
                info = await contract_interface.get_market_info(market_id)
                
                if info["resolved"]:
                    continue
                if info["deadline"] >= datetime.now().timestamp():
                    continue
                
                final_price = await self.get_price(info["symbol"])
                final_price_cents = int(final_price * 100)
                
                await contract_interface.resolve_market(market_id, final_price_cents)
                print(f"Resolved market {market_id}: {info['symbol']} at ${final_price}")
                
            except Exception as e:
                print(f"Error resolving market {market_id}: {e}")


async def test_oracle() -> None:
    """Test the price oracle."""
    oracle = PriceOracle()
    
    print("Testing Price Oracle...")
    
    for symbol in ["BTC", "ETH"]:
        try:
            price = await oracle.get_price(symbol)
            print(f"{symbol}: ${price:,.2f}")
        except Exception as e:
            print(f"{symbol}: Error - {e}")


if __name__ == "__main__":
    asyncio.run(test_oracle())
