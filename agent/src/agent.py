"""Main agent wrapper for programmatic use."""
import asyncio
from typing import Optional

from langchain_core.messages import HumanMessage

from config import config
from setup import setup_async


class PredictionMarketAgent:
    """Main agent for interacting with prediction markets."""
    
    def __init__(self):
        self.config = config
        self.agent_executor = None
        self.agent_config: Optional[dict] = None
    
    async def initialize(self) -> None:
        """Initialize the agent and its components."""
        self.agent_executor, self.agent_config, _ = await setup_async()
    
    async def run(self, user_input: str) -> str:
        """Run the agent with user input and return response."""
        if not self.agent_executor:
            await self.initialize()
        
        result = await self.agent_executor.ainvoke(
            {"messages": [HumanMessage(content=user_input)]},
            self.agent_config
        )
        
        if isinstance(result, dict) and "messages" in result:
            return result["messages"][-1].content
        return str(result)
    
    async def stream(self, user_input: str):
        """Stream responses from the agent."""
        if not self.agent_executor:
            await self.initialize()
        
        async for chunk in self.agent_executor.astream(
            {"messages": [HumanMessage(content=user_input)]},
            self.agent_config
        ):
            yield chunk


async def main() -> None:
    """Main entry point for quick CLI usage."""
    agent = PredictionMarketAgent()
    await agent.initialize()
    
    print("Prediction Market Agent initialized on Base Sepolia.")
    print("Type 'quit' or 'exit' to stop.\n")
    
    while True:
        try:
            user_input = input("> ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["quit", "exit"]:
                break
            
            response = await agent.run(user_input)
            print(f"\nAgent: {response}\n")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    asyncio.run(main())
