import sys
import time
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from setup import setup

"""
AgentKit Chatbot Interface

This file provides a command-line interface for interacting with your AgentKit-powered AI agent.
It supports two modes of operation: interactive chat and autonomous mode for periodic tasks.
"""

load_dotenv()


# Autonomous Mode
def run_autonomous_mode(agent_executor, config, interval=10):
    """Run the agent autonomously with specified intervals."""
    print("Starting autonomous mode...")
    while True:
        try:
            thought = (
                "Be creative and do something interesting on the blockchain. "
                "Choose an action or set of actions and execute it that highlights your abilities."
            )

            for chunk in agent_executor.stream({"messages": [HumanMessage(content=thought)]}, config):
                if "agent" in chunk:
                    print(chunk["agent"]["messages"][0].content)
                elif "tools" in chunk:
                    print(chunk["tools"]["messages"][0].content)
                print("-------------------")

            time.sleep(interval)

        except KeyboardInterrupt:
            print("Goodbye Agent!")
            sys.exit(0)


# Chat Mode
def run_chat_mode(agent_executor, config):
    """Run the agent interactively based on user input."""
    print("Starting chat mode... Type 'exit' to end.")
    while True:
        try:
            user_input = input("\nPrompt: ")
            if user_input.lower() == "exit":
                break

            for chunk in agent_executor.stream({"messages": [HumanMessage(content=user_input)]}, config):
                if "agent" in chunk:
                    print(chunk["agent"]["messages"][0].content)
                elif "tools" in chunk:
                    print(chunk["tools"]["messages"][0].content)
                print("-------------------")

        except KeyboardInterrupt:
            print("Goodbye Agent!")
            sys.exit(0)


# Mode Selection
def choose_mode():
    """Choose whether to run in autonomous or chat mode based on user input."""
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


def main():
    load_dotenv()
    try:
        agent_executor, agent_config, _wallet_provider = setup()
    except ValueError as exc:
        print(f"Configuration error: {exc}")
        sys.exit(1)

    print("\nWelcome to the CDP Agent Chatbot!")
    print("Type 'exit' to quit the chat.\n")

    mode = choose_mode()
    if mode == "chat":
        run_chat_mode(agent_executor=agent_executor, config=agent_config)
    elif mode == "auto":
        run_autonomous_mode(agent_executor=agent_executor, config=agent_config)


if __name__ == "__main__":
    print("Starting Agent...")
    main()
