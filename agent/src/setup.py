"""Entry point to wire up the Prediction Market agent."""
import asyncio
from typing import Any
from unittest.mock import MagicMock

from web3 import Web3

from config import config
from contract_interface import PredictionMarketContract
from initialize_agent import build_agent, build_agentkit
from market_actions import MarketActions


def _is_valid_ethereum_address(address: str | None) -> bool:
    """Check if the address is a valid Ethereum address."""
    if not address:
        return False
    
    invalid_patterns = ["...", "your_", "placeholder"]
    if any(p in address.lower() for p in invalid_patterns):
        return False
    
    try:
        Web3.to_checksum_address(address)
        return True
    except (ValueError, TypeError):
        return False


def _validate_config() -> None:
    """Validate required configuration."""
    missing = config.validate_required()
    
    if config.contract_address and not _is_valid_ethereum_address(config.contract_address):
        missing.append("CONTRACT_ADDRESS (must be a valid Ethereum address)")
    
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")


def _create_market_actions(agentkit) -> MarketActions:
    """Create market actions with contract if available."""
    if config.has_valid_contract:
        try:
            contract = PredictionMarketContract(
                agent_kit=agentkit,
                contract_address=config.contract_address,
                rpc_url=config.base_sepolia_rpc_url,
            )
            return MarketActions(contract)
        except Exception as e:
            print(f"Warning: Could not initialize contract: {e}")
    
    print("Warning: No valid contract address. Contract actions unavailable.")
    print("To deploy: cd ../contracts && npx hardhat run scripts/deploy.js --network base-sepolia")
    return MarketActions(None)


async def setup_async() -> tuple[Any, dict, Any]:
    """Build the agent asynchronously."""
    _validate_config()
    
    agentkit, wallet_provider = await build_agentkit(config)
    market_actions = _create_market_actions(agentkit)
    
    executor, graph_config, wallet_provider = await build_agent(
        config, market_actions, agentkit=agentkit, wallet_provider=wallet_provider
    )
    return executor, graph_config, wallet_provider


def setup() -> tuple[Any, dict, Any]:
    """Synchronous wrapper for chatbot.py."""
    return asyncio.run(setup_async())
