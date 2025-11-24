# tests/test_agent.py
import os
import sys
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
from dotenv import load_dotenv

# Add src to path without triggering __init__.py imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Import only the specific modules we need
from config import Config


class TestAgentInitialization:
    """Test cases for agent initialization."""

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
    def mock_config(self):
        """Create a mock configuration for testing."""
        return Config(
            cdp_api_key_name="test_key_name",
            cdp_private_key="test_private_key",
            llm_provider="glm",
            glm_api_key="test_glm_key",
            model="glm-4.6",
            base_url="https://api.z.ai/api/paas/v4/"
        )

    @pytest.mark.asyncio
    async def test_build_agentkit(self, mock_config):
        """Test building the AgentKit instance."""
        # Mock the coinbase_agentkit module
        with patch.dict('sys.modules', {
            'coinbase_agentkit': MagicMock(
                AgentKit=MagicMock(),
                AgentKitConfig=MagicMock(),
                CdpEvmWalletProvider=MagicMock(),
                CdpEvmWalletProviderConfig=MagicMock(),
                cdp_api_action_provider=MagicMock(),
                erc20_action_provider=MagicMock(),
                pyth_action_provider=MagicMock(),
                wallet_action_provider=MagicMock(),
                weth_action_provider=MagicMock(),
            )
        }):
            from initialize_agent import build_agentkit
            
            mock_wallet_instance = MagicMock()
            mock_agentkit_instance = MagicMock()
            
            with patch('initialize_agent.CdpEvmWalletProvider', return_value=mock_wallet_instance), \
                 patch('initialize_agent.AgentKit', return_value=mock_agentkit_instance):
                
                agentkit, wallet_provider = await build_agentkit(mock_config)
                
                assert agentkit is not None
                assert wallet_provider is not None

    @pytest.mark.asyncio
    async def test_build_agent_with_glm(self, mock_config):
        """Test building the agent with GLM configuration."""
        with patch.dict('sys.modules', {
            'coinbase_agentkit': MagicMock(
                AgentKit=MagicMock(),
                AgentKitConfig=MagicMock(),
                CdpEvmWalletProvider=MagicMock(),
                CdpEvmWalletProviderConfig=MagicMock(),
                cdp_api_action_provider=MagicMock(),
                erc20_action_provider=MagicMock(),
                pyth_action_provider=MagicMock(),
                wallet_action_provider=MagicMock(),
                weth_action_provider=MagicMock(),
            ),
            'coinbase_agentkit_langchain': MagicMock(
                get_langchain_tools=MagicMock(return_value=[])
            )
        }):
            from initialize_agent import build_agent
            
            mock_market_actions = MagicMock()
            mock_market_actions.get_tools.return_value = [MagicMock()]
            
            mock_agentkit = MagicMock()
            mock_wallet_provider = MagicMock()
            
            mock_client = MagicMock()
            mock_llm = MagicMock()
            mock_memory_instance = MagicMock()
            mock_executor = MagicMock()
            
            with patch('initialize_agent.OpenAI', return_value=mock_client), \
                 patch('initialize_agent.ChatOpenAI', return_value=mock_llm), \
                 patch('initialize_agent.MemorySaver', return_value=mock_memory_instance), \
                 patch('initialize_agent.create_react_agent', return_value=mock_executor), \
                 patch('initialize_agent.get_langchain_tools', return_value=[]):
                
                executor, graph_config, wallet_provider = await build_agent(
                    mock_config, mock_market_actions, agentkit=mock_agentkit, wallet_provider=mock_wallet_provider
                )
                
                assert executor == mock_executor
                assert graph_config == {"configurable": {"thread_id": "prediction-market"}}
                assert wallet_provider == mock_wallet_provider

    @pytest.mark.asyncio
    async def test_build_agent_with_openai_fallback(self):
        """Test building the agent with OpenAI fallback configuration."""
        with patch.dict('sys.modules', {
            'coinbase_agentkit': MagicMock(
                AgentKit=MagicMock(),
                AgentKitConfig=MagicMock(),
                CdpEvmWalletProvider=MagicMock(),
                CdpEvmWalletProviderConfig=MagicMock(),
                cdp_api_action_provider=MagicMock(),
                erc20_action_provider=MagicMock(),
                pyth_action_provider=MagicMock(),
                wallet_action_provider=MagicMock(),
                weth_action_provider=MagicMock(),
            ),
            'coinbase_agentkit_langchain': MagicMock(
                get_langchain_tools=MagicMock(return_value=[])
            )
        }):
            from initialize_agent import build_agent
            
            openai_config = Config(
                cdp_api_key_name="test_key_name",
                cdp_private_key="test_private_key",
                llm_provider="openai",
                openai_api_key="test_openai_key",
                model="gpt-4"
            )
            
            mock_market_actions = MagicMock()
            mock_market_actions.get_tools.return_value = [MagicMock()]
            
            mock_agentkit = MagicMock()
            mock_wallet_provider = MagicMock()
            
            mock_llm = MagicMock()
            mock_memory_instance = MagicMock()
            mock_executor = MagicMock()
            
            with patch('initialize_agent.ChatOpenAI', return_value=mock_llm) as mock_chat_openai, \
                 patch('initialize_agent.OpenAI') as mock_openai, \
                 patch('initialize_agent.MemorySaver', return_value=mock_memory_instance), \
                 patch('initialize_agent.create_react_agent', return_value=mock_executor), \
                 patch('initialize_agent.get_langchain_tools', return_value=[]):
                
                executor, graph_config, wallet_provider = await build_agent(
                    openai_config, mock_market_actions, agentkit=mock_agentkit, wallet_provider=mock_wallet_provider
                )
                
                mock_openai.assert_not_called()
                
                mock_chat_openai.assert_called_once_with(
                    model="gpt-4",
                    api_key="test_openai_key",
                    temperature=0
                )
                
                assert executor == mock_executor
                assert graph_config == {"configurable": {"thread_id": "prediction-market"}}
                assert wallet_provider == mock_wallet_provider

    def test_config_initialization(self, mock_config):
        """Test that the config is properly initialized."""
        assert mock_config.llm_provider == "glm"
        assert mock_config.model == "glm-4.6"
        assert mock_config.glm_api_key == "test_glm_key"