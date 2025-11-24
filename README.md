# Prediction Market Agent

An AI-powered prediction market agent built with Coinbase AgentKit that can interact with smart contracts on Base Sepolia.

## Features

- AI agent powered by LangChain and OpenAI
- Smart contract interaction on Base Sepolia
- Price oracle integration
- Market creation and betting functionality

## Setup

1. Clone the repository
2. Create a virtual environment:
  
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   3. Install dependencies:
  
   cd agent
   pip install -r requirements.txt
   4. Configure environment variables:
  
   cp .env.example .env
   # Edit .env with your API keys
   5. Compile contracts:
  
   cd ../contracts
   npm install
   npx hardhat compile
   6. Run the agent:
  
   cd ../agent
   python src/chatbot.py
   ## Environment Variables

Required:
- `CDP_API_KEY_NAME` - Coinbase Developer Platform API key name
- `CDP_API_PRIVATE_KEY` - Coinbase Developer Platform private key
- `OPENAI_API_KEY` - OpenAI API key
- `CONTRACT_ADDRESS` - Deployed contract address
- `BASE_SEPOLIA_RPC_URL` - Base Sepolia RPC URL

## Architecture

- `agent/` - Python agent code
- `contracts/` - Solidity smart contracts
- `docs/` - Documentation

## License

MIT
