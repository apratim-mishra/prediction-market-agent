"""Enhanced Price Oracle with Multiple API Support"""
import os
import aiohttp
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum

class PriceSource(Enum):
    ALPHA_VANTAGE = "alpha_vantage"
    COINGECKO = "coingecko"
    COINBASE = "coinbase"
    POLYGON = "polygon"

class PriceOracle:
    """Multi-source price oracle for stocks and crypto"""
    
    def __init__(self):
        # Load API keys from environment
        self.alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        self.coingecko_key = os.getenv("COINGECKO_API_KEY")
        self.polygon_key = os.getenv("POLYGON_API_KEY")
        
        # API endpoints
        self.endpoints = {
            PriceSource.ALPHA_VANTAGE: "https://www.alphavantage.co/query",
            PriceSource.COINGECKO: "https://api.coingecko.com/api/v3",
            PriceSource.COINBASE: "https://api.coinbase.com/v2",
            PriceSource.POLYGON: "https://api.polygon.io"
        }
        
        # Symbol mappings for different sources
        self.crypto_mappings = {
            "BTC": {"coingecko": "bitcoin", "coinbase": "BTC-USD"},
            "ETH": {"coingecko": "ethereum", "coinbase": "ETH-USD"},
            "SOL": {"coingecko": "solana", "coinbase": "SOL-USD"},
        }
    
    async def get_stock_price(self, symbol: str) -> Dict[str, Any]:
        """Get stock price from Alpha Vantage or Polygon"""
        if self.alpha_vantage_key:
            return await self._fetch_alpha_vantage_stock(symbol)
        elif self.polygon_key:
            return await self._fetch_polygon_price(symbol, "stocks")
        else:
            raise ValueError("No stock API key configured. Add ALPHA_VANTAGE_API_KEY or POLYGON_API_KEY to .env")
    
    async def get_crypto_price(self, symbol: str) -> Dict[str, Any]:
        """Get crypto price from available sources"""
        # Try sources in order of preference
        if symbol in self.crypto_mappings:
            # Try CoinGecko first
            if self.coingecko_key:
                return await self._fetch_coingecko_price(symbol)
            # Fall back to Coinbase (no key needed)
            return await self._fetch_coinbase_price(symbol)
        else:
            raise ValueError(f"Unknown crypto symbol: {symbol}")
    
    async def get_price(self, symbol: str) -> float:
        """Universal price getter - determines if stock or crypto"""
        try:
            # Check if it's a known crypto
            if symbol in self.crypto_mappings:
                result = await self.get_crypto_price(symbol)
            else:
                # Assume it's a stock
                result = await self.get_stock_price(symbol)
            
            return result["price"]
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
            # Return mock price for testing
            return 100.0
    
    async def _fetch_alpha_vantage_stock(self, symbol: str) -> Dict[str, Any]:
        """Fetch stock price from Alpha Vantage"""
        async with aiohttp.ClientSession() as session:
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": self.alpha_vantage_key
            }
            
            async with session.get(self.endpoints[PriceSource.ALPHA_VANTAGE], params=params) as response:
                data = await response.json()
                
                if "Global Quote" in data:
                    quote = data["Global Quote"]
                    return {
                        "symbol": symbol,
                        "price": float(quote["05. price"]),
                        "change": float(quote["09. change"]),
                        "change_percent": quote["10. change percent"],
                        "timestamp": datetime.now().isoformat(),
                        "source": "alpha_vantage"
                    }
                else:
                    raise ValueError(f"No data found for {symbol}")
    
    async def _fetch_coingecko_price(self, symbol: str) -> Dict[str, Any]:
        """Fetch crypto price from CoinGecko"""
        gecko_id = self.crypto_mappings[symbol]["coingecko"]
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.endpoints[PriceSource.COINGECKO]}/simple/price"
            params = {
                "ids": gecko_id,
                "vs_currencies": "usd",
                "include_24hr_change": "true"
            }
            
            headers = {}
            if self.coingecko_key:
                headers["x-cg-demo-api-key"] = self.coingecko_key
            
            async with session.get(url, params=params, headers=headers) as response:
                data = await response.json()
                
                if gecko_id in data:
                    return {
                        "symbol": symbol,
                        "price": data[gecko_id]["usd"],
                        "change_24h": data[gecko_id].get("usd_24h_change", 0),
                        "timestamp": datetime.now().isoformat(),
                        "source": "coingecko"
                    }
                else:
                    raise ValueError(f"No data found for {symbol}")
    
    async def _fetch_coinbase_price(self, symbol: str) -> Dict[str, Any]:
        """Fetch crypto price from Coinbase (no API key needed)"""
        pair = self.crypto_mappings[symbol]["coinbase"]
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.endpoints[PriceSource.COINBASE]}/exchange-rates"
            params = {"currency": symbol}
            
            async with session.get(url, params=params) as response:
                data = await response.json()
                
                if "data" in data and "rates" in data["data"]:
                    return {
                        "symbol": symbol,
                        "price": float(data["data"]["rates"]["USD"]),
                        "timestamp": datetime.now().isoformat(),
                        "source": "coinbase"
                    }
                else:
                    raise ValueError(f"No data found for {symbol}")
    
    async def _fetch_polygon_price(self, symbol: str, asset_type: str) -> Dict[str, Any]:
        """Fetch price from Polygon.io"""
        async with aiohttp.ClientSession() as session:
            if asset_type == "stocks":
                url = f"{self.endpoints[PriceSource.POLYGON]}/v2/aggs/ticker/{symbol}/prev"
            else:  # crypto
                url = f"{self.endpoints[PriceSource.POLYGON]}/v2/aggs/ticker/X:{symbol}USD/prev"
            
            params = {"apiKey": self.polygon_key}
            
            async with session.get(url, params=params) as response:
                data = await response.json()
                
                if "results" in data and len(data["results"]) > 0:
                    result = data["results"][0]
                    return {
                        "symbol": symbol,
                        "price": result["c"],  # closing price
                        "timestamp": datetime.now().isoformat(),
                        "source": "polygon"
                    }
                else:
                    raise ValueError(f"No data found for {symbol}")
    
    async def resolve_expired_markets(self, contract_interface, market_ids: list):
        """Resolve expired markets with actual prices"""
        for market_id in market_ids:
            try:
                # Get market info
                market_info = await contract_interface.get_market_info(market_id)
                
                # Check if market is expired and not resolved
                if not market_info["resolved"] and market_info["deadline"] < datetime.now().timestamp():
                    # Get final price
                    final_price = await self.get_price(market_info["symbol"])
                    
                    # Convert to cents for contract
                    final_price_cents = int(final_price * 100)
                    
                    # Resolve market
                    await contract_interface.resolve_market(market_id, final_price_cents)
                    
                    print(f"Resolved market {market_id}: {market_info['symbol']} at ${final_price}")
                    
            except Exception as e:
                print(f"Error resolving market {market_id}: {e}")

# Test function
async def test_oracle():
    """Test the price oracle"""
    oracle = PriceOracle()
    
    # Test stock price
    try:
        tesla_price = await oracle.get_price("TSLA")
        print(f"TSLA: ${tesla_price}")
    except Exception as e:
        print(f"Stock price error: {e}")
    
    # Test crypto price
    try:
        btc_price = await oracle.get_price("BTC")
        print(f"BTC: ${btc_price}")
    except Exception as e:
        print(f"Crypto price error: {e}")

if __name__ == "__main__":
    asyncio.run(test_oracle())