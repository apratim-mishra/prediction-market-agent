# src/config.py

"""Configuration management for Prediction Market Agent"""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from both repo root and agent folder to reduce setup friction
_HERE = Path(__file__).resolve().parent
_AGENT_DIR = _HERE.parent  # agent/ directory
_ROOT_DIR = _AGENT_DIR.parent  # prediction-market-agent/ directory

# Try loading from multiple locations
env_files = [
    _AGENT_DIR / ".env",           # agent/.env
    _AGENT_DIR / ".env.local",     # agent/.env.local
    _ROOT_DIR / ".env",            # prediction-market-agent/.env
    Path.cwd() / ".env",           # Current working directory
]

for env_file in env_files:
    if env_file.exists():
        load_dotenv(env_file, override=False)  # Don't override if already set
        break

# Also try loading from current directory as fallback
load_dotenv(override=False)


@dataclass
class Config:
    """Configuration for the Prediction Market Agent"""

    # CDP Configuration
    cdp_api_key_name: str
    cdp_private_key: str
    cdp_wallet_secret: str
    network_id: str = "base-sepolia"

    # Contract Configuration
    contract_address: Optional[str] = None
    base_sepolia_rpc_url: Optional[str] = None

    # LLM Configuration
    llm_provider: str = "glm"  # "openai" or "glm"
    openai_api_key: str = ""
    glm_api_key: str = ""
    model: str = "glm-4.6"
    base_url: str = "https://api.z.ai/api/paas/v4/"

    # Optional data sources
    price_api_key: Optional[str] = None

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables"""
        # Debug: Print loaded values (remove in production)
        wallet_secret = os.getenv("CDP_WALLET_SECRET", "")
        if not wallet_secret:
            print(f"Warning: CDP_WALLET_SECRET not found in environment")
            print(f"Checked .env files: {[str(f) for f in env_files]}")
            print(f"Current working directory: {Path.cwd()}")
        
        return cls(
            cdp_api_key_name=os.getenv("CDP_API_KEY_NAME", ""),
            cdp_private_key=os.getenv("CDP_API_PRIVATE_KEY", ""),
            cdp_wallet_secret=wallet_secret,
            network_id=os.getenv("NETWORK_ID", "base-sepolia"),
            contract_address=os.getenv("CONTRACT_ADDRESS"),
            base_sepolia_rpc_url=os.getenv("BASE_SEPOLIA_RPC_URL"),
            llm_provider=os.getenv("LLM_PROVIDER", "glm"),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            glm_api_key=os.getenv("GLM_API_KEY", ""),
            model=os.getenv("MODEL", "glm-4.6"),
            base_url=os.getenv("BASE_URL", "https://api.z.ai/api/paas/v4/"),
            price_api_key=os.getenv("PRICE_API_KEY"),
        )


config = Config.from_env()