# src/setup.py

"""Entry point to wire up the Prediction Market agent."""
import asyncio
from typing import Tuple
from web3 import Web3

from config import config
from contract_interface import PredictionMarketContract
from initialize_agent import build_agent, build_agentkit
from market_actions import MarketActions


def _is_valid_ethereum_address(address: str) -> bool:
    """Check if the address is a valid Ethereum address (not a placeholder)."""
    if not address:
        return False
    # Check for common placeholder patterns
    if "..." in address or "your_" in address.lower() or "placeholder" in address.lower():
        return False
    # Check if it's a valid hex address
    try:
        Web3.to_checksum_address(address)
        return True
    except (ValueError, TypeError):
        return False


def _validate_config():
    missing = []
    if not config.cdp_api_key_name:
        missing.append("CDP_API_KEY_NAME")
    if not config.cdp_private_key:
        missing.append("CDP_API_PRIVATE_KEY")
    if not config.cdp_wallet_secret:
        missing.append("CDP_WALLET_SECRET")
    if not config.openai_api_key and not config.glm_api_key:
        missing.append("OPENAI_API_KEY or GLM_API_KEY")
    
    # Check contract address - make it optional but validate if provided
    if config.contract_address:
        if not _is_valid_ethereum_address(config.contract_address):
            missing.append("CONTRACT_ADDRESS (must be a valid Ethereum address, not a placeholder)")
    # Contract address is optional - agent can work without it for basic operations
    
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")


async def setup_async() -> Tuple[object, dict, object]:
    """Build the agent asynchronously."""
    _validate_config()
    agentkit, wallet_provider = await build_agentkit(config)
    
    # Only create contract interface if address is valid
    contract = None
    if config.contract_address and _is_valid_ethereum_address(config.contract_address):
        contract = PredictionMarketContract(
            agent_kit=agentkit,
            contract_address=config.contract_address,
            rpc_url=config.base_sepolia_rpc_url,
        )
    else:
        # Create a mock/placeholder contract for testing
        # The agent can still work for basic operations without a deployed contract
        print("Warning: No valid contract address provided. Contract-specific actions will not be available.")
        print("To deploy the contract, run: cd ../contracts && npx hardhat run scripts/deploy.js --network base-sepolia")
        # Create a minimal contract interface that won't fail
        contract = None
    
    market_actions = MarketActions(contract) if contract else None
    if not market_actions:
        # Create a minimal market actions that won't fail
        from unittest.mock import MagicMock
        market_actions = MagicMock()
        market_actions.get_tools = lambda: []
    
    executor, graph_config, wallet_provider = await build_agent(
        config, market_actions, agentkit=agentkit, wallet_provider=wallet_provider
    )
    return executor, graph_config, wallet_provider


def setup():
    """Synchronous wrapper so chatbot.py can import without managing asyncio."""
    return asyncio.run(setup_async())