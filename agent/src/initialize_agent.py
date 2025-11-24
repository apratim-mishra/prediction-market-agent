"""AgentKit bootstrapping helpers using the Coinbase AgentKit libraries."""
from typing import Tuple

from coinbase_agentkit import (
    AgentKit,
    CdpWalletProvider,
    cdp_api_action_provider,
    erc20_action_provider,
    pyth_action_provider,
    wallet_action_provider,
    weth_action_provider,
)
from coinbase_agentkit_langchain import get_langchain_tools
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from config import Config
from market_actions import MarketActions

AGENT_INSTRUCTIONS = (
    "You are a helpful agent that can interact onchain using the Coinbase Developer Platform AgentKit. "
    "You can deploy and call contracts on Base Sepolia. If you need funds, request them from the faucet "
    "or ask the user to provide them. Before using any tool, confirm the active network and wallet "
    "address. Keep responses concise and focus on clear next steps."
)


async def build_agentkit(cfg: Config) -> Tuple[AgentKit, CdpWalletProvider]:
    """Construct an AgentKit instance with standard action providers."""
    wallet_provider = CdpWalletProvider(
        api_key_name=cfg.cdp_api_key_name,
        private_key=cfg.cdp_private_key,
        network_id=cfg.network_id,
    )
    action_providers = [
        cdp_api_action_provider(),
        erc20_action_provider(),
        pyth_action_provider(),
        wallet_action_provider(),
        weth_action_provider(),
    ]

    # AgentKit.from_config is async; AgentKit(...) is sync. Prefer from_config when available.
    if hasattr(AgentKit, "from_config"):
        agentkit = await AgentKit.from_config(
            {"wallet_provider": wallet_provider, "network_id": cfg.network_id, "action_providers": action_providers}
        )
    else:
        agentkit = AgentKit(wallet_provider=wallet_provider, action_providers=action_providers)

    # Attach standard CDP action providers in case they were not added during construction
    if hasattr(agentkit, "add_action_providers"):
        agentkit.add_action_providers(action_providers)
    elif hasattr(agentkit, "action_providers"):
        agentkit.action_providers = action_providers
    return agentkit, wallet_provider


async def build_agent(
    cfg: Config, market_actions: MarketActions, agentkit: AgentKit | None = None, wallet_provider=None
):
    """Create the LangGraph agent executor plus default config."""
    if agentkit is None or wallet_provider is None:
        agentkit, wallet_provider = await build_agentkit(cfg)
    tools = get_langchain_tools(agentkit) + market_actions.get_tools()

    llm = ChatOpenAI(model=cfg.model, api_key=cfg.openai_api_key, temperature=0)
    memory = MemorySaver()

    executor = create_react_agent(
        llm,
        tools=tools,
        checkpointer=memory,
        state_modifier=AGENT_INSTRUCTIONS,
    )
    # LangGraph expects a thread id for stateful runs
    graph_config = {"configurable": {"thread_id": "prediction-market"}}
    return executor, graph_config, wallet_provider
