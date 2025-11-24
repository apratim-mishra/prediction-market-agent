# Prediction Market Agent (Python)

Chatbot powered by CDP AgentKit Core + LangGraph that can call the PredictionMarket contract on Base Sepolia.

## Setup

1. Create a virtualenv (Python 3.11+) and install deps:
   ```sh
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Copy `./agent/.env.example` to `./agent/.env` and fill:
   - `CDP_API_KEY_NAME` and `CDP_API_PRIVATE_KEY`
   - `CONTRACT_ADDRESS` (after you deploy with Hardhat)
   - `OPENAI_API_KEY`
   - `BASE_SEPOLIA_RPC_URL` (Alchemy recommended)
3. Run the chatbot:
   ```sh
   python src/chatbot.py
   ```

## Notes

- Tools come from CDP AgentKit core plus custom tools for the PredictionMarket contract.
- Ensure the contract is compiled (`cd ../contracts && npx hardhat compile`) so the ABI is available to the agent.
