"""AgentKit bootstrapping helpers using the Coinbase AgentKit libraries."""
from typing import Any

from coinbase_agentkit import (
    AgentKit,
    AgentKitConfig,
    CdpEvmWalletProvider,
    CdpEvmWalletProviderConfig,
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


AGENT_INSTRUCTIONS = """You are a helpful agent that can interact onchain using the Coinbase Developer Platform AgentKit.
You can deploy and call contracts on Base Sepolia. If you need funds, request them from the faucet or ask the user to provide them.
Before using any tool, confirm the active network and wallet address. Keep responses concise and focus on clear next steps."""


async def build_agentkit(cfg: Config) -> tuple[AgentKit, CdpEvmWalletProvider]:
    """Construct an AgentKit instance with standard action providers."""
    wallet_provider = CdpEvmWalletProvider(
        CdpEvmWalletProviderConfig(
            api_key_id=cfg.cdp_api_key_name,
            api_key_secret=cfg.cdp_private_key,
            wallet_secret=cfg.cdp_wallet_secret,
            network_id=cfg.network_id,
        )
    )
    
    action_providers = [
        cdp_api_action_provider(),
        erc20_action_provider(),
        pyth_action_provider(),
        wallet_action_provider(),
        weth_action_provider(),
    ]
    
    agentkit = AgentKit(
        AgentKitConfig(
            wallet_provider=wallet_provider,
            action_providers=action_providers
        )
    )
    
    return agentkit, wallet_provider


def _create_llm(cfg: Config) -> ChatOpenAI:
    """Create the LLM based on configuration."""
    if cfg.llm_provider == "glm":
        return ChatOpenAI(
            model=cfg.model,
            api_key=cfg.glm_api_key,
            base_url=cfg.base_url,
            temperature=0,
        )
    return ChatOpenAI(
        model=cfg.model,
        api_key=cfg.openai_api_key,
        temperature=0
    )


async def build_agent(
    cfg: Config,
    market_actions: MarketActions,
    agentkit: AgentKit | None = None,
    wallet_provider: CdpEvmWalletProvider | None = None
) -> tuple[Any, dict, CdpEvmWalletProvider]:
    """Create the LangGraph agent executor with configuration."""
    if agentkit is None or wallet_provider is None:
        agentkit, wallet_provider = await build_agentkit(cfg)
    
    tools = get_langchain_tools(agentkit) + market_actions.get_tools()
    llm = _create_llm(cfg)
    llm_with_instructions = llm.bind(system=AGENT_INSTRUCTIONS)
    memory = MemorySaver()
    
    executor = create_react_agent(
        llm_with_instructions,
        tools=tools,
        checkpointer=memory,
    )
    
    graph_config = {"configurable": {"thread_id": "prediction-market"}}
    return executor, graph_config, wallet_provider
