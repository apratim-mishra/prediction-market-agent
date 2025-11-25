"""Tests for the Config class."""
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import Config


class TestConfig:
    """Test cases for the Config class."""

    @pytest.fixture(autouse=True)
    def setup_env(self):
        """Set up environment variables for testing."""
        load_dotenv()
        env_keys = [
            "CDP_API_KEY_NAME", "CDP_API_PRIVATE_KEY", "CDP_WALLET_SECRET",
            "LLM_PROVIDER", "MODEL", "GLM_API_KEY", "OPENAI_API_KEY", "BASE_URL"
        ]
        self.original_env = {k: os.environ.get(k) for k in env_keys}
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
            cdp_private_key="test_private_key",
            cdp_wallet_secret="test_secret"
        )
        
        assert cfg.llm_provider == "glm"
        assert cfg.model == "glm-4.6"
        assert cfg.base_url == "https://api.z.ai/api/paas/v4/"
        assert cfg.network_id == "base-sepolia"

    @patch.dict(os.environ, {
        "CDP_API_KEY_NAME": "env_key_name",
        "CDP_API_PRIVATE_KEY": "env_private_key",
        "CDP_WALLET_SECRET": "env_secret",
        "LLM_PROVIDER": "openai",
        "MODEL": "gpt-4",
        "GLM_API_KEY": "test_glm_key"
    }, clear=False)
    def test_from_env(self):
        """Test loading configuration from environment variables."""
        cfg = Config.from_env()
        
        assert cfg.cdp_api_key_name == "env_key_name"
        assert cfg.cdp_private_key == "env_private_key"
        assert cfg.cdp_wallet_secret == "env_secret"
        assert cfg.llm_provider == "openai"
        assert cfg.model == "gpt-4"
        assert cfg.glm_api_key == "test_glm_key"

    def test_validate_required_missing(self):
        """Test validation reports missing required fields."""
        cfg = Config()
        missing = cfg.validate_required()
        
        assert "CDP_API_KEY_NAME" in missing
        assert "CDP_API_PRIVATE_KEY" in missing
        assert "CDP_WALLET_SECRET" in missing
        assert "OPENAI_API_KEY or GLM_API_KEY" in missing

    def test_validate_required_complete(self):
        """Test validation passes with all required fields."""
        cfg = Config(
            cdp_api_key_name="key",
            cdp_private_key="private",
            cdp_wallet_secret="secret",
            glm_api_key="glm_key"
        )
        missing = cfg.validate_required()
        
        assert len(missing) == 0

    def test_has_valid_contract_empty(self):
        """Test has_valid_contract with no address."""
        cfg = Config()
        assert not cfg.has_valid_contract

    def test_has_valid_contract_placeholder(self):
        """Test has_valid_contract with placeholder address."""
        cfg = Config(contract_address="your_contract_address")
        assert not cfg.has_valid_contract

    def test_has_valid_contract_valid(self):
        """Test has_valid_contract with valid address."""
        cfg = Config(
            contract_address="0x1234567890123456789012345678901234567890"
        )
        assert cfg.has_valid_contract
