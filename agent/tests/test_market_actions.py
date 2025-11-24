# tests/test_market_actions.py
import os
import sys
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from dotenv import load_dotenv

# Add src to path without triggering __init__.py imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Import only the specific modules we need
from market_actions import MarketActions


class TestMarketActions:
    """Test cases for market actions."""

    @pytest.fixture(autouse=True)
    def setup_env(self):
        """Set up environment variables for testing."""
        load_dotenv()
        
        self.original_env = {}
        for key in [
            "CDP_API_KEY_NAME", "CDP_API_PRIVATE_KEY", "LLM_PROVIDER", 
            "MODEL", "GLM_API_KEY", "OPENAI_API_KEY", "BASE_URL"
        ]:
            self.original_env[key] = os.environ.get(key)
        
        yield
        
        for key, value in self.original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    @pytest.fixture
    def mock_contract(self):
        """Create a mock contract for testing."""
        contract = MagicMock()
        return contract

    def test_market_actions_initialization(self, mock_contract):
        """Test that MarketActions initializes correctly."""
        market_actions = MarketActions(mock_contract)
        assert market_actions.contract == mock_contract

    def test_get_tools(self, mock_contract):
        """Test that get_tools returns the expected tools."""
        market_actions = MarketActions(mock_contract)
        tools = market_actions.get_tools()
        
        # Verify that tools is a list
        assert isinstance(tools, list)
        
        # Verify that each tool has the expected attributes
        for tool in tools:
            assert hasattr(tool, 'name')
            assert hasattr(tool, 'description')
            assert callable(tool.func)

    @patch.dict(os.environ, {
        "CONTRACT_ADDRESS": "0x1234567890123456789012345678901234567890",
        "BASE_SEPOLIA_RPC_URL": "https://base-sepolia-rpc.example.com"
    }, clear=False)
    def test_market_actions_with_env_config(self):
        """Test MarketActions with configuration loaded from environment variables."""
        # Create a mock contract with environment configuration
        contract = MagicMock()
        
        # Create MarketActions instance
        market_actions = MarketActions(contract)
        
        # Verify initialization
        assert market_actions.contract == contract
        
        # Test that tools can be retrieved
        tools = market_actions.get_tools()
        assert isinstance(tools, list)