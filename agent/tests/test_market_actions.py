"""Tests for market actions."""
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from market_actions import MarketActions, CreateMarketInput, PlaceBetInput


class TestMarketActions:
    """Test cases for market actions."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        load_dotenv()

    @pytest.fixture
    def mock_contract(self):
        """Create a mock contract for testing."""
        contract = MagicMock()
        contract.create_market = AsyncMock(return_value={
            "market_id": 1,
            "tx_hash": "0xabc123"
        })
        contract.place_bet = AsyncMock(return_value={
            "success": True,
            "tx_hash": "0xdef456",
            "market_id": 1,
            "prediction": "UP",
            "amount": 0.1
        })
        contract.get_market_info = AsyncMock(return_value={
            "symbol": "BTC",
            "target_price": 50000.0,
            "deadline": 1700000000,
            "total_up_bets": 1.5,
            "total_down_bets": 1.0,
            "resolved": False,
            "outcome": None,
            "final_price": None
        })
        contract.claim_winnings = AsyncMock(return_value={
            "market_id": 1,
            "tx_hash": "0xghi789"
        })
        return contract

    def test_initialization(self, mock_contract):
        """Test that MarketActions initializes correctly."""
        actions = MarketActions(mock_contract)
        assert actions.contract == mock_contract

    def test_initialization_without_contract(self):
        """Test initialization without a contract."""
        actions = MarketActions(None)
        assert actions.contract is None

    def test_get_tools_with_contract(self, mock_contract):
        """Test that get_tools returns tools when contract is available."""
        actions = MarketActions(mock_contract)
        tools = actions.get_tools()
        
        assert isinstance(tools, list)
        assert len(tools) == 4
        
        tool_names = [t.name for t in tools]
        assert "create_market" in tool_names
        assert "place_bet" in tool_names
        assert "get_market_info" in tool_names
        assert "claim_winnings" in tool_names

    def test_get_tools_without_contract(self):
        """Test that get_tools returns empty list without contract."""
        actions = MarketActions(None)
        tools = actions.get_tools()
        
        assert tools == []

    def test_tool_has_required_attributes(self, mock_contract):
        """Test that each tool has required attributes."""
        actions = MarketActions(mock_contract)
        tools = actions.get_tools()
        
        for tool in tools:
            assert hasattr(tool, "name")
            assert hasattr(tool, "description")
            assert hasattr(tool, "func")
            assert callable(tool.func)

    @pytest.mark.asyncio
    async def test_create_market(self, mock_contract):
        """Test creating a market."""
        actions = MarketActions(mock_contract)
        result = await actions._create_market("BTC", 50000.0, 24)
        
        assert "Market created successfully" in result
        assert "Market ID: 1" in result
        mock_contract.create_market.assert_called_once_with("BTC", 5000000, 24)

    @pytest.mark.asyncio
    async def test_place_bet_up(self, mock_contract):
        """Test placing an UP bet."""
        actions = MarketActions(mock_contract)
        result = await actions._place_bet(1, "UP", 0.1)
        
        assert "Bet placed successfully" in result
        mock_contract.place_bet.assert_called_once_with(1, True, 0.1)

    @pytest.mark.asyncio
    async def test_place_bet_down(self, mock_contract):
        """Test placing a DOWN bet."""
        actions = MarketActions(mock_contract)
        await actions._place_bet(1, "DOWN", 0.1)
        
        mock_contract.place_bet.assert_called_once_with(1, False, 0.1)

    @pytest.mark.asyncio
    async def test_get_market_info(self, mock_contract):
        """Test getting market info."""
        actions = MarketActions(mock_contract)
        result = await actions._get_market_info(1)
        
        assert "Market 1 - BTC" in result
        assert "Target Price: $50000.0" in result
        assert "Status: Active" in result

    @pytest.mark.asyncio
    async def test_claim_winnings(self, mock_contract):
        """Test claiming winnings."""
        actions = MarketActions(mock_contract)
        result = await actions._claim_winnings(1)
        
        assert "Winnings claimed successfully" in result
        mock_contract.claim_winnings.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_create_market_error(self, mock_contract):
        """Test error handling in create_market."""
        mock_contract.create_market = AsyncMock(side_effect=Exception("Network error"))
        actions = MarketActions(mock_contract)
        
        result = await actions._create_market("BTC", 50000.0, 24)
        
        assert "Failed to create market" in result
        assert "Network error" in result


class TestInputSchemas:
    """Test input schema validation."""

    def test_create_market_input(self):
        """Test CreateMarketInput schema."""
        input_data = CreateMarketInput(
            symbol="BTC",
            target_price=50000.0,
            duration_hours=24
        )
        assert input_data.symbol == "BTC"
        assert input_data.target_price == 50000.0
        assert input_data.duration_hours == 24

    def test_place_bet_input(self):
        """Test PlaceBetInput schema."""
        input_data = PlaceBetInput(
            market_id=1,
            prediction="UP",
            amount_eth=0.1
        )
        assert input_data.market_id == 1
        assert input_data.prediction == "UP"
        assert input_data.amount_eth == 0.1
