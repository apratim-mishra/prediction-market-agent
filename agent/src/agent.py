"""Main agent wrapper for programmatic use."""
import asyncio

from langchain_core.messages import HumanMessage

from config import config
from setup import setup_async


class PredictionMarketAgent:
    """Main agent for interacting with prediction markets."""

    def __init__(self):
        self.config = config
        self.agent_executor = None
        self.agent_config = None

    async def initialize(self):
        """Initialize the agent and its components."""
        self.agent_executor, self.agent_config, _wallet_provider = await setup_async()

    async def run(self, user_input: str) -> str:
        """Run the agent with user input."""
        if not self.agent_executor:
            await self.initialize()

        result = await self.agent_executor.ainvoke(
            {"messages": [HumanMessage(content=user_input)]}, self.agent_config
        )
        if isinstance(result, dict) and "messages" in result:
            return result["messages"][-1].content
        return str(result)


async def main():
    """Main entry point for quick CLI usage."""
    agent = PredictionMarketAgent()
    await agent.initialize()

    print("Prediction Market Agent initialized on Base Sepolia.")
    while True:
        user_input = input("\n> ")
        if user_input.lower() in ["quit", "exit"]:
            break

        response = await agent.run(user_input)
        print(f"\nAgent: {response}")


if __name__ == "__main__":
    asyncio.run(main())
