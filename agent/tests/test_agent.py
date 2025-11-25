"""Tests for agent initialization."""
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import importlib.util

import pytest
from dotenv import load_dotenv

# Ensure src is in path
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from config import Config


def load_module_from_file(module_name: str, file_path: str):
    """Load a module directly from a file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class TestAgentInitialization:
    """Test cases for agent initialization."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        load_dotenv()

    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration for testing."""
        return Config(
            cdp_api_key_name="test_key_name",
            cdp_private_key="test_private_key",
            cdp_wallet_secret="test_secret",
            llm_provider="glm",
            glm_api_key="test_glm_key",
            model="glm-4.6",
            base_url="https://api.z.ai/api/paas/v4/"
        )

    @pytest.mark.asyncio
    async def test_build_agentkit_mocked(self, mock_config):
        """Test building the AgentKit instance with full mocking."""
        mock_wallet = MagicMock()
        mock_agentkit = MagicMock()
        
        with patch("initialize_agent.CdpEvmWalletProvider", return_value=mock_wallet), \
             patch("initialize_agent.CdpEvmWalletProviderConfig"), \
             patch("initialize_agent.AgentKit", return_value=mock_agentkit), \
             patch("initialize_agent.AgentKitConfig"):
            
            from initialize_agent import build_agentkit
            agentkit, wallet_provider = await build_agentkit(mock_config)
            
            assert agentkit == mock_agentkit
            assert wallet_provider == mock_wallet

    @pytest.mark.asyncio
    async def test_build_agent_with_glm(self, mock_config):
        """Test building the agent with GLM configuration."""
        mock_agentkit = MagicMock()
        mock_wallet = MagicMock()
        mock_llm = MagicMock()
        mock_executor = MagicMock()
        
        mock_market_actions = MagicMock()
        mock_market_actions.get_tools.return_value = []
        
        with patch("initialize_agent.get_langchain_tools", return_value=[]), \
             patch("initialize_agent.ChatOpenAI", return_value=mock_llm), \
             patch("initialize_agent.MemorySaver"), \
             patch("initialize_agent.create_react_agent", return_value=mock_executor):
            
            from initialize_agent import build_agent
            executor, graph_config, wallet = await build_agent(
                mock_config, mock_market_actions, 
                agentkit=mock_agentkit, wallet_provider=mock_wallet
            )
            
            assert executor == mock_executor
            assert "configurable" in graph_config
            assert graph_config["configurable"]["thread_id"] == "prediction-market"

    @pytest.mark.asyncio
    async def test_build_agent_with_openai(self):
        """Test building the agent with OpenAI configuration."""
        openai_config = Config(
            cdp_api_key_name="test_key_name",
            cdp_private_key="test_private_key",
            cdp_wallet_secret="test_secret",
            llm_provider="openai",
            openai_api_key="test_openai_key",
            model="gpt-4"
        )
        
        mock_agentkit = MagicMock()
        mock_wallet = MagicMock()
        mock_llm = MagicMock()
        mock_executor = MagicMock()
        
        mock_market_actions = MagicMock()
        mock_market_actions.get_tools.return_value = []
        
        with patch("initialize_agent.get_langchain_tools", return_value=[]), \
             patch("initialize_agent.ChatOpenAI", return_value=mock_llm) as mock_chat, \
             patch("initialize_agent.MemorySaver"), \
             patch("initialize_agent.create_react_agent", return_value=mock_executor):
            
            from initialize_agent import build_agent
            await build_agent(
                openai_config, mock_market_actions,
                agentkit=mock_agentkit, wallet_provider=mock_wallet
            )
            
            mock_chat.assert_called_once_with(
                model="gpt-4",
                api_key="test_openai_key",
                temperature=0
            )


class TestPredictionMarketAgent:
    """Test cases for the PredictionMarketAgent class."""

    @pytest.fixture
    def mock_executor(self):
        """Create a mock executor."""
        mock = MagicMock()
        mock.ainvoke = AsyncMock(return_value={
            "messages": [MagicMock(content="Test response")]
        })
        return mock

    @pytest.fixture
    def agent_module_path(self):
        """Get the path to the agent.py module."""
        return str(Path(__file__).parent.parent / "src" / "agent.py")

    @pytest.mark.asyncio
    async def test_agent_initialize(self, mock_executor, agent_module_path):
        """Test agent initialization."""
        mock_config = {"configurable": {"thread_id": "test"}}
        mock_wallet = MagicMock()
        
        with patch("setup.setup_async", new=AsyncMock(
            return_value=(mock_executor, mock_config, mock_wallet)
        )):
            # Load module directly from file
            agent_mod = load_module_from_file("agent_src", agent_module_path)
            
            pm_agent = agent_mod.PredictionMarketAgent()
            assert pm_agent.agent_executor is None
            
            await pm_agent.initialize()
            
            assert pm_agent.agent_executor == mock_executor
            assert pm_agent.agent_config == mock_config

    @pytest.mark.asyncio
    async def test_agent_run(self, mock_executor, agent_module_path):
        """Test running the agent."""
        mock_config = {"configurable": {"thread_id": "test"}}
        mock_wallet = MagicMock()
        
        with patch("setup.setup_async", new=AsyncMock(
            return_value=(mock_executor, mock_config, mock_wallet)
        )):
            agent_mod = load_module_from_file("agent_src_run", agent_module_path)
            
            pm_agent = agent_mod.PredictionMarketAgent()
            response = await pm_agent.run("What is my wallet address?")
            
            assert response == "Test response"
            mock_executor.ainvoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_agent_run_non_dict_response(self, mock_executor, agent_module_path):
        """Test agent run with non-dict response."""
        mock_executor.ainvoke = AsyncMock(return_value="Direct response")
        mock_config = {"configurable": {"thread_id": "test"}}
        mock_wallet = MagicMock()
        
        with patch("setup.setup_async", new=AsyncMock(
            return_value=(mock_executor, mock_config, mock_wallet)
        )):
            agent_mod = load_module_from_file("agent_src_non_dict", agent_module_path)
            
            pm_agent = agent_mod.PredictionMarketAgent()
            response = await pm_agent.run("test")
            
            assert response == "Direct response"
