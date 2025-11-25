"""AgentKit Chatbot Interface.

Provides a command-line interface for interacting with the AgentKit-powered AI agent.
Supports interactive chat mode and autonomous mode for periodic blockchain tasks.
"""
import sys
import time

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from setup import setup


load_dotenv()


def run_autonomous_mode(agent_executor, config: dict, interval: int = 10) -> None:
    """Run the agent autonomously with specified intervals."""
    print("Starting autonomous mode...")
    thought = (
        "Be creative and do something interesting on the blockchain. "
        "Choose an action or set of actions that highlights your abilities."
    )
    
    while True:
        try:
            for chunk in agent_executor.stream(
                {"messages": [HumanMessage(content=thought)]}, config
            ):
                _print_chunk(chunk)
            time.sleep(interval)
        except KeyboardInterrupt:
            print("\nGoodbye Agent!")
            sys.exit(0)


def run_chat_mode(agent_executor, config: dict) -> None:
    """Run the agent interactively based on user input."""
    print("Starting chat mode... Type 'exit' to end.")
    
    while True:
        try:
            user_input = input("\nPrompt: ").strip()
            if not user_input:
                continue
            if user_input.lower() == "exit":
                break
            
            for chunk in agent_executor.stream(
                {"messages": [HumanMessage(content=user_input)]}, config
            ):
                _print_chunk(chunk)
        except KeyboardInterrupt:
            print("\nGoodbye Agent!")
            sys.exit(0)


def _print_chunk(chunk: dict) -> None:
    """Print a chunk from the agent stream."""
    if "agent" in chunk:
        print(chunk["agent"]["messages"][0].content)
    elif "tools" in chunk:
        print(chunk["tools"]["messages"][0].content)
    print("-------------------")


def choose_mode() -> str:
    """Choose between autonomous or chat mode."""
    while True:
        print("\nAvailable modes:")
        print("1. chat    - Interactive chat mode")
        print("2. auto    - Autonomous action mode")
        
        choice = input("\nChoose a mode (enter number or name): ").lower().strip()
        if choice in ["1", "chat"]:
            return "chat"
        if choice in ["2", "auto"]:
            return "auto"
        print("Invalid choice. Please try again.")


def main() -> None:
    """Main entry point for the chatbot."""
    load_dotenv()
    
    try:
        agent_executor, agent_config, _ = setup()
    except ValueError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)
    
    print("\nWelcome to the CDP Agent Chatbot!")
    print("Type 'exit' to quit the chat.\n")
    
    mode = choose_mode()
    if mode == "chat":
        run_chat_mode(agent_executor, agent_config)
    else:
        run_autonomous_mode(agent_executor, agent_config)


if __name__ == "__main__":
    print("Starting Agent...")
    main()
