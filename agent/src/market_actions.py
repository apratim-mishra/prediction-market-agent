"""Market actions for the Prediction Market Agent."""
import asyncio
from typing import Optional

from langchain_core.tools import Tool
from pydantic import BaseModel, Field

from contract_interface import PredictionMarketContract


class CreateMarketInput(BaseModel):
    """Input schema for creating a market."""
    symbol: str = Field(description="Asset symbol (e.g., TSLA or BTC)")
    target_price: float = Field(description="Target price in USD")
    duration_hours: int = Field(description="Duration in hours (max 168)")


class PlaceBetInput(BaseModel):
    """Input schema for placing a bet."""
    market_id: int = Field(description="Market ID to bet on")
    prediction: str = Field(description="Prediction: 'UP' or 'DOWN'")
    amount_eth: float = Field(description="Amount to bet in ETH")


class GetMarketInfoInput(BaseModel):
    """Input schema for getting market info."""
    market_id: int = Field(description="Market ID to query")


class ClaimWinningsInput(BaseModel):
    """Input schema for claiming winnings."""
    market_id: int = Field(description="Market ID to claim from")


class MarketActions:
    """Actions for interacting with prediction markets."""
    
    def __init__(self, contract: Optional[PredictionMarketContract]):
        self.contract = contract
    
    def _create_async_tool(
        self,
        name: str,
        description: str,
        coro,
        schema: type[BaseModel]
    ) -> Tool:
        """Create a tool that supports both sync and async execution."""
        def sync_wrapper(*args, **kwargs):
            return asyncio.run(coro(*args, **kwargs))
        
        return Tool(
            name=name,
            description=description,
            func=sync_wrapper,
            coroutine=coro,
            args_schema=schema,
        )
    
    def get_tools(self) -> list[Tool]:
        """Get LangChain tools for market actions."""
        if not self.contract:
            return []
        
        return [
            self._create_async_tool(
                name="create_market",
                description="Create a new prediction market for an asset price",
                coro=self._create_market,
                schema=CreateMarketInput,
            ),
            self._create_async_tool(
                name="place_bet",
                description="Place a bet on whether an asset price will go UP or DOWN",
                coro=self._place_bet,
                schema=PlaceBetInput,
            ),
            self._create_async_tool(
                name="get_market_info",
                description="Get information about a specific market",
                coro=self._get_market_info,
                schema=GetMarketInfoInput,
            ),
            self._create_async_tool(
                name="claim_winnings",
                description="Claim winnings from a resolved market",
                coro=self._claim_winnings,
                schema=ClaimWinningsInput,
            ),
        ]
    
    async def _create_market(
        self,
        symbol: str,
        target_price: float,
        duration_hours: int
    ) -> str:
        """Create a new market."""
        try:
            target_price_cents = int(target_price * 100)
            result = await self.contract.create_market(
                symbol, target_price_cents, duration_hours
            )
            return (
                f"Market created successfully! "
                f"Market ID: {result['market_id']}, "
                f"Transaction: {result['tx_hash']}"
            )
        except Exception as e:
            return f"Failed to create market: {e}"
    
    async def _place_bet(
        self,
        market_id: int,
        prediction: str,
        amount_eth: float
    ) -> str:
        """Place a bet on a market."""
        try:
            prediction_bool = prediction.strip().upper() == "UP"
            result = await self.contract.place_bet(
                market_id, prediction_bool, amount_eth
            )
            return (
                f"Bet placed successfully! "
                f"You bet {amount_eth} ETH on {prediction.upper()} "
                f"for market {market_id}. "
                f"Transaction: {result['tx_hash']}"
            )
        except Exception as e:
            return f"Failed to place bet: {e}"
    
    async def _get_market_info(self, market_id: int) -> str:
        """Get market information."""
        try:
            info = await self.contract.get_market_info(market_id)
            status = "Resolved" if info["resolved"] else "Active"
            outcome = info["outcome"] if info["resolved"] else "Pending"
            final_price = f"${info['final_price']}" if info["final_price"] else "N/A"
            
            return (
                f"Market {market_id} - {info['symbol']}:\n"
                f"- Target Price: ${info['target_price']}\n"
                f"- Total UP Bets: {info['total_up_bets']} ETH\n"
                f"- Total DOWN Bets: {info['total_down_bets']} ETH\n"
                f"- Status: {status}\n"
                f"- Outcome: {outcome}\n"
                f"- Final Price: {final_price}"
            )
        except Exception as e:
            return f"Failed to get market info: {e}"
    
    async def _claim_winnings(self, market_id: int) -> str:
        """Claim winnings from a market."""
        try:
            result = await self.contract.claim_winnings(market_id)
            return f"Winnings claimed successfully! Transaction: {result['tx_hash']}"
        except Exception as e:
            return f"Failed to claim winnings: {e}"
