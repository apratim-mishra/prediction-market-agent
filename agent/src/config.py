"""Configuration management for Prediction Market Agent"""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from both repo root and agent folder to reduce setup friction
_HERE = Path(__file__).resolve().parent
load_dotenv(_HERE.parent / ".env")
load_dotenv(_HERE.parent / ".env.local")
load_dotenv()  # fallback to current working directory


@dataclass
class Config:
    """Configuration for the Prediction Market Agent"""

    # CDP Configuration
    cdp_api_key_name: str
    cdp_private_key: str
    network_id: str = "base-sepolia"

    # Contract Configuration
    contract_address: Optional[str] = None
    base_sepolia_rpc_url: Optional[str] = None

    # OpenAI Configuration
    openai_api_key: str = ""
    model: str = "gpt-4o-mini"

    # Optional data sources
    price_api_key: Optional[str] = None

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables"""
        return cls(
            cdp_api_key_name=os.getenv("CDP_API_KEY_NAME", ""),
            cdp_private_key=os.getenv("CDP_API_PRIVATE_KEY", ""),
            network_id=os.getenv("NETWORK_ID", "base-sepolia"),
            contract_address=os.getenv("CONTRACT_ADDRESS"),
            base_sepolia_rpc_url=os.getenv("BASE_SEPOLIA_RPC_URL"),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            price_api_key=os.getenv("PRICE_API_KEY"),
        )


config = Config.from_env()
