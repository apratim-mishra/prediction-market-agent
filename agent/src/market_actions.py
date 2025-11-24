"""Market actions for the Prediction Market Agent"""
import asyncio
from typing import List

from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import Tool

from contract_interface import PredictionMarketContract


class CreateMarketInput(BaseModel):
    """Input for creating a market"""

    symbol: str = Field(description="Asset symbol (e.g., TSLA or BTC)")
    target_price: float = Field(description="Target price in USD")
    duration_hours: int = Field(description="Duration in hours (max 168)")


class PlaceBetInput(BaseModel):
    """Input for placing a bet"""

    market_id: int = Field(description="Market ID to bet on")
    prediction: str = Field(description="Prediction: 'UP' or 'DOWN'")
    amount_eth: float = Field(description="Amount to bet in ETH")


class MarketActions:
    """Actions for interacting with prediction markets"""

    def __init__(self, contract: PredictionMarketContract):
        self.contract = contract

    def _async_tool(self, *, name: str, description: str, schema=None, coro=None) -> Tool:
        """Create a tool that supports both sync and async execution."""

        def _blocking(*args, **kwargs):
            return asyncio.run(coro(*args, **kwargs))

        return Tool(
            name=name,
            description=description,
            func=_blocking if coro else None,
            coroutine=coro,
            args_schema=schema,
        )

    def get_tools(self) -> List[Tool]:
        """Get LangChain tools for market actions"""
        return [
            self._async_tool(
                name="create_market",
                description="Create a new prediction market for an asset price",
                schema=CreateMarketInput,
                coro=self._create_market,
            ),
            self._async_tool(
                name="place_bet",
                description="Place a bet on whether an asset price will go UP or DOWN",
                schema=PlaceBetInput,
                coro=self._place_bet,
            ),
            self._async_tool(
                name="get_market_info",
                description="Get information about a specific market",
                coro=self._get_market_info,
            ),
            self._async_tool(
                name="claim_winnings",
                description="Claim winnings from a resolved market",
                coro=self._claim_winnings,
            ),
        ]

    async def _create_market(self, symbol: str, target_price: float, duration_hours: int) -> str:
        """Create a new market"""
        try:
            target_price_cents = int(target_price * 100)
            result = await self.contract.create_market(symbol, target_price_cents, duration_hours)
            return f"Market created successfully! Market ID: {result['market_id']}, Transaction: {result['tx_hash']}"
        except Exception as exc:
            return f"Failed to create market: {exc}"

    async def _place_bet(self, market_id: int, prediction: str, amount_eth: float) -> str:
        """Place a bet on a market"""
        try:
            prediction_bool = prediction.strip().upper() == "UP"
            result = await self.contract.place_bet(market_id, prediction_bool, amount_eth)
            return (
                f"Bet placed successfully! You bet {amount_eth} ETH on {prediction.upper()} for market {market_id}. "
                f"Transaction: {result['tx_hash']}"
            )
        except Exception as exc:
            return f"Failed to place bet: {exc}"

    async def _get_market_info(self, market_id: int) -> str:
        """Get market information"""
        try:
            info = await self.contract.get_market_info(market_id)
            return (
                f"Market {market_id} - {info['symbol']}:\n"
                f"- Target Price: ${info['target_price']}\n"
                f"- Total UP Bets: {info['total_up_bets']} ETH\n"
                f"- Total DOWN Bets: {info['total_down_bets']} ETH\n"
                f"- Status: {'Resolved' if info['resolved'] else 'Active'}\n"
                f"- Outcome: {info['outcome'] if info['resolved'] else 'Pending'}\n"
                f"- Final Price: ${info['final_price'] if info['final_price'] else 'N/A'}"
            )
        except Exception as exc:
            return f"Failed to get market info: {exc}"

    async def _claim_winnings(self, market_id: int) -> str:
        """Claim winnings from a market"""
        try:
            result = await self.contract.claim_winnings(market_id)
            return f"Winnings claimed successfully! Transaction: {result['tx_hash']}"
        except Exception as exc:
            return f"Failed to claim winnings: {exc}"
