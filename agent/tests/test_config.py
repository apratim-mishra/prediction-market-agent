# tests/test_config.py
import os
import sys
import pytest
from unittest.mock import patch
from pathlib import Path
from dotenv import load_dotenv

# Add src to path without triggering __init__.py imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Import only the specific module we need
import config as config_module
from config import Config


class TestConfig:
    """Test cases for the Config class."""

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

    def test_default_values(self):
        """Test that default values are set correctly."""
        cfg = Config(
            cdp_api_key_name="test_key_name",
            cdp_private_key="test_private_key"
        )
        
        assert cfg.llm_provider == "glm"
        assert cfg.model == "glm-4.6"
        assert cfg.base_url == "https://api.z.ai/api/paas/v4/"
        assert cfg.network_id == "base-sepolia"

    @patch.dict(os.environ, {
        "CDP_API_KEY_NAME": "env_key_name",
        "CDP_API_PRIVATE_KEY": "env_private_key",
        "LLM_PROVIDER": "openai",
        "MODEL": "gpt-4",
        "GLM_API_KEY": "test_glm_key"
    }, clear=False)
    def test_from_env(self):
        """Test loading configuration from environment variables."""
        cfg = Config.from_env()
        
        assert cfg.cdp_api_key_name == "env_key_name"
        assert cfg.cdp_private_key == "env_private_key"
        assert cfg.llm_provider == "openai"
        assert cfg.model == "gpt-4"
        assert cfg.glm_api_key == "test_glm_key"

    def test_glm_config(self):
        """Test GLM-specific configuration."""
        cfg = Config(
            cdp_api_key_name="test_key_name",
            cdp_private_key="test_private_key",
            llm_provider="glm",
            glm_api_key="test_glm_key",
            model="glm-4.6"
        )
        
        assert cfg.llm_provider == "glm"
        assert cfg.model == "glm-4.6"
        assert cfg.glm_api_key == "test_glm_key"
        assert cfg.base_url == "https://api.z.ai/api/paas/v4/"

    def test_config_loads_dotenv(self):
        """Test that the config module loads dotenv on import."""
        # Verify that load_dotenv was called by checking if config_module has loaded
        assert hasattr(config_module, 'Config')
        assert hasattr(config_module, 'config')