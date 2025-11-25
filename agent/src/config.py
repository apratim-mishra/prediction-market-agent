"""Configuration management for Prediction Market Agent."""
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


def _load_env_files() -> None:
    """Load environment variables from multiple possible locations."""
    here = Path(__file__).resolve().parent
    agent_dir = here.parent
    root_dir = agent_dir.parent
    
    env_locations = [
        agent_dir / ".env",
        agent_dir / ".env.local",
        root_dir / ".env",
        Path.cwd() / ".env",
    ]
    
    for env_file in env_locations:
        if env_file.exists():
            load_dotenv(env_file, override=False)
            break
    
    load_dotenv(override=False)


_load_env_files()


@dataclass
class Config:
    """Configuration for the Prediction Market Agent."""
    
    # CDP Configuration (required)
    cdp_api_key_name: str = ""
    cdp_private_key: str = ""
    cdp_wallet_secret: str = ""
    network_id: str = "base-sepolia"
    
    # Contract Configuration (optional)
    contract_address: Optional[str] = None
    base_sepolia_rpc_url: Optional[str] = None
    
    # LLM Configuration
    llm_provider: str = "glm"
    openai_api_key: str = ""
    glm_api_key: str = ""
    model: str = "glm-4.6"
    base_url: str = "https://api.z.ai/api/paas/v4/"
    
    # Optional data sources
    price_api_key: Optional[str] = None
    alpha_vantage_api_key: Optional[str] = None
    coingecko_api_key: Optional[str] = None
    polygon_api_key: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        return cls(
            cdp_api_key_name=os.getenv("CDP_API_KEY_NAME", ""),
            cdp_private_key=os.getenv("CDP_API_PRIVATE_KEY", ""),
            cdp_wallet_secret=os.getenv("CDP_WALLET_SECRET", ""),
            network_id=os.getenv("NETWORK_ID", "base-sepolia"),
            contract_address=os.getenv("CONTRACT_ADDRESS"),
            base_sepolia_rpc_url=os.getenv("BASE_SEPOLIA_RPC_URL"),
            llm_provider=os.getenv("LLM_PROVIDER", "glm"),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            glm_api_key=os.getenv("GLM_API_KEY", ""),
            model=os.getenv("MODEL", "glm-4.6"),
            base_url=os.getenv("BASE_URL", "https://api.z.ai/api/paas/v4/"),
            price_api_key=os.getenv("PRICE_API_KEY"),
            alpha_vantage_api_key=os.getenv("ALPHA_VANTAGE_API_KEY"),
            coingecko_api_key=os.getenv("COINGECKO_API_KEY"),
            polygon_api_key=os.getenv("POLYGON_API_KEY"),
        )
    
    def validate_required(self) -> list[str]:
        """Return list of missing required configuration keys."""
        missing = []
        if not self.cdp_api_key_name:
            missing.append("CDP_API_KEY_NAME")
        if not self.cdp_private_key:
            missing.append("CDP_API_PRIVATE_KEY")
        if not self.cdp_wallet_secret:
            missing.append("CDP_WALLET_SECRET")
        if not self.openai_api_key and not self.glm_api_key:
            missing.append("OPENAI_API_KEY or GLM_API_KEY")
        return missing
    
    @property
    def has_valid_contract(self) -> bool:
        """Check if a valid contract address is configured."""
        if not self.contract_address:
            return False
        invalid_patterns = ["...", "your_", "placeholder", "0x0000"]
        return not any(p in self.contract_address.lower() for p in invalid_patterns)


config = Config.from_env()
