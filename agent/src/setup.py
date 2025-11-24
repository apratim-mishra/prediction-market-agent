"""Entry point to wire up the Prediction Market agent."""
import asyncio
from typing import Tuple

from config import config
from contract_interface import PredictionMarketContract
from initialize_agent import build_agent, build_agentkit
from market_actions import MarketActions


def _validate_config():
    missing = []
    if not config.cdp_api_key_name:
        missing.append("CDP_API_KEY_NAME")
    if not config.cdp_private_key:
        missing.append("CDP_API_PRIVATE_KEY")
    if not config.openai_api_key:
        missing.append("OPENAI_API_KEY")
    if not config.contract_address:
        missing.append("CONTRACT_ADDRESS")
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")


async def setup_async() -> Tuple[object, dict, object]:
    """Build the agent asynchronously."""
    _validate_config()
    agentkit, wallet_provider = await build_agentkit(config)
    contract = PredictionMarketContract(
        agent_kit=agentkit,
        contract_address=config.contract_address,
        rpc_url=config.base_sepolia_rpc_url,
    )
    market_actions = MarketActions(contract)
    executor, graph_config, wallet_provider = await build_agent(
        config, market_actions, agentkit=agentkit, wallet_provider=wallet_provider
    )
    return executor, graph_config, wallet_provider


def setup():
    """Synchronous wrapper so chatbot.py can import without managing asyncio."""
    return asyncio.run(setup_async())
