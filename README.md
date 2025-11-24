# Prediction Market Agent

An AI-powered prediction market agent built with Coinbase AgentKit that can interact with smart contracts on Base Sepolia testnet. The agent supports both OpenAI and GLM-4.6 language models.

## Features

- 🤖 AI agent powered by LangChain and LangGraph
- 🔗 Smart contract interaction on Base Sepolia testnet
- 💰 Coinbase Developer Platform (CDP) wallet integration
- 📊 Price oracle integration for real-time asset prices
- 🎯 Market creation and betting functionality
- 🌐 Support for multiple LLM providers (OpenAI GPT-4, GLM-4.6)
- 🧪 Comprehensive test suite with pytest

## Architecture

prediction-market-agent/
├── agent/ # Python agent code
│ ├── src/ # Source code
│ │ ├── agent.py # Main agent wrapper
│ │ ├── chatbot.py # Interactive chatbot interface
│ │ ├── config.py # Configuration management
│ │ ├── contract_interface.py # Smart contract interface
│ │ ├── initialize_agent.py # Agent initialization
│ │ ├── market_actions.py # Market-specific actions
│ │ └── price_oracle.py # Price oracle integration
│ ├── tests/ # Test suite
│ └── requirements.txt # Python dependencies
├── contracts/ # Solidity smart contracts
│ ├── contracts/ # Contract source files
│ ├── scripts/ # Deployment scripts
│ └── test/ # Contract tests
└── docs/ # Documentation

## Prerequisites

- Python 3.11+
- Node.js 16+
- [CDP API Keys](https://docs.cdp.coinbase.com/get-started/docs/cdp-api-keys)
- GLM API Key (from [Z.AI](https://z.ai)) or OpenAI API Key

## Setup

### 1. Clone the repository

git clone <your-repo-url>
cd prediction-market-agent### 2. Create a virtual environment

python -m venv .venv
source .venv/bin/activate # On Windows: .venv\Scripts\activate### 3. Install Python dependencies

cd agent
pip install -r requirements.txt### 4. Configure environment variables

cp .env.example .envEdit `.env` with your credentials:

# CDP Configuration

CDP_API_KEY_NAME=your-cdp-api-key-name
CDP_API_PRIVATE_KEY=your-cdp-private-key
CDP_WALLET_SECRET=your-cdp-wallet-secret
NETWORK_ID=base-sepolia

# Contract Configuration (optional - can be set after deployment)

CONTRACT_ADDRESS=
BASE_SEPOLIA_RPC_URL=your-base-sepolia-rpc-url

# LLM Configuration

LLM_PROVIDER=glm # or "openai"
GLM_API_KEY=your-z-ai-api-key
MODEL=glm-4.6
BASE_URL=https://api.z.ai/api/paas/v4/

# Optional: OpenAI Configuration (fallback)

OPENAI_API_KEY=your-openai-api-key

# Optional data sources

PRICE_API_KEY=your-price-api-key### 5. Compile smart contracts

cd ../contracts
npm install
npx hardhat compile### 6. Deploy contracts (optional)

npx hardhat run scripts/deploy.js --network base-sepolia

# Copy the deployed contract address to your .env file### 7. Run the agent

cd ../agent
python src/chatbot.py## Usage

The agent supports two modes:

### Chat Mode (Interactive)

python src/chatbot.py

# Choose option 1 for chat modeExample prompts:

- `What is my wallet address?`
- `Request testnet funds from the faucet`
- `What's the current price of Tesla stock?`
- `Create a prediction market for BTC at $95000 for 48 hours`
- `Place a 0.01 ETH bet on market 0 predicting UP`

### Autonomous Mode

python src/chatbot.py

# Choose option 2 for autonomous modeThe agent will periodically execute blockchain actions autonomously.

## Testing

Run the test suite:

cd agent
pytest -vRun specific tests:

pytest tests/test_config.py -v
pytest tests/test_agent.py -v
pytest tests/test_market_actions.py -v## Environment Variables

### Required

- `CDP_API_KEY_NAME` - Coinbase Developer Platform API key name
- `CDP_API_PRIVATE_KEY` - Coinbase Developer Platform API key secret
- `CDP_WALLET_SECRET` - CDP wallet secret for authentication
- `GLM_API_KEY` or `OPENAI_API_KEY` - LLM provider API key

### Optional

- `CONTRACT_ADDRESS` - Deployed prediction market contract address
- `BASE_SEPOLIA_RPC_URL` - Base Sepolia RPC endpoint (e.g., Alchemy)
- `LLM_PROVIDER` - Choose between "glm" or "openai" (default: "glm")
- `MODEL` - Model name (default: "glm-4.6")
- `PRICE_API_KEY` - API key for price oracle services

## Getting API Keys

### CDP API Keys

1. Go to [Coinbase Developer Platform](https://portal.cdp.coinbase.com/)
2. Create a new project
3. Generate API keys (API Key Name and API Key Secret)
4. Generate a Wallet Secret in the Server Wallet section

### GLM API Key

1. Visit [Z.AI](https://z.ai)
2. Sign up for an account
3. Generate an API key from your dashboard

### OpenAI API Key (Alternative)

1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create an account and generate an API key

## Smart Contract

The prediction market contract is deployed on Base Sepolia testnet. Key features:

- Create prediction markets for any asset with target price and duration
- Place bets (UP/DOWN) with ETH
- Automatic market resolution based on oracle prices
- Claim winnings after market resolution

## Development

### Code Style

The project follows clean code principles:

- Modular, Pythonic code
- Minimal comments (self-documenting code)
- Basic error handling
- Type hints where appropriate

### Project Structure

- `agent/src/` - Core agent implementation
- `agent/tests/` - Test suite
- `contracts/` - Solidity smart contracts
- `docs/` - Additional documentation

## Troubleshooting

### Common Issues

1. **"Missing required environment variables"**

   - Ensure all required variables are set in `.env`
   - Check that `.env` file is in the `agent/` directory

2. **"Failed to initialize CDP wallet"**

   - Verify your CDP API credentials
   - Ensure CDP_WALLET_SECRET is generated from CDP dashboard

3. **"Contract address not set"**

   - Deploy the contract first or comment out CONTRACT_ADDRESS in `.env`
   - The agent can run without a contract for basic wallet operations

4. **GLM API connection issues**
   - Verify your GLM_API_KEY is correct
   - Check that BASE_URL is set to `https://api.z.ai/api/paas/v4/`
   - Alternatively, switch to OpenAI by setting `LLM_PROVIDER=openai`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT

## Resources

- [Coinbase Developer Platform Docs](https://docs.cdp.coinbase.com/)
- [AgentKit Documentation](https://github.com/coinbase/agentkit)
- [Base Sepolia Testnet](https://docs.base.org/network-information)
- [LangChain Documentation](https://python.langchain.com/)
- [Z.AI Documentation](https://z.ai/docs)
