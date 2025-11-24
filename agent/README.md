# Prediction Market Agent (Python)

AI-powered chatbot built with CDP AgentKit Core + LangGraph that interacts with the PredictionMarket smart contract on Base Sepolia testnet.

## Features

- 🤖 Powered by GLM-4.6 or OpenAI GPT models
- 💰 CDP wallet integration for seamless blockchain operations
- 📊 Real-time price oracle integration
- 🎯 Create and manage prediction markets
- 💸 Place bets and claim winnings
- 🔧 Comprehensive test suite

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment (Python 3.11+)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env
```

Edit `.env` with your credentials:

```bash
# Required: CDP Configuration
CDP_API_KEY_NAME=your-cdp-api-key-name
CDP_API_PRIVATE_KEY=your-cdp-private-key
CDP_WALLET_SECRET=your-cdp-wallet-secret
NETWORK_ID=base-sepolia

# Required: LLM Configuration
LLM_PROVIDER=glm  # or "openai"
GLM_API_KEY=your-z-ai-api-key
MODEL=glm-4.6
BASE_URL=https://api.z.ai/api/paas/v4/

# Optional: OpenAI fallback
OPENAI_API_KEY=your-openai-api-key

# Optional: Contract (set after deployment)
CONTRACT_ADDRESS=
BASE_SEPOLIA_RPC_URL=your-base-sepolia-rpc-url
```

### 3. Compile Contract (First Time Only)

```bash
cd ../contracts
npm install
npx hardhat compile
```

### 4. Run the Agent

```bash
python src/chatbot.py
```

## Usage Modes

### Interactive Chat Mode

```bash
python src/chatbot.py
# Select option 1: chat
```

**Example Commands:**
- `What is my wallet address?`
- `Request testnet funds from the faucet`
- `What's the current price of Tesla stock?`
- `Create a prediction market for BTC at $95000 for 48 hours`
- `Place a 0.01 ETH bet on market 0 predicting UP`
- `Get information about market 0`
- `Claim winnings from market 0`

### Autonomous Mode

```bash
python src/chatbot.py
# Select option 2: auto
```

The agent will autonomously execute blockchain actions at regular intervals.

## Testing

Run all tests:

```bash
pytest -v
```

Run specific test files:

```bash
pytest tests/test_config.py -v      # Configuration tests
pytest tests/test_agent.py -v       # Agent initialization tests
pytest tests/test_market_actions.py -v  # Market actions tests
```

## Project Structure

```
agent/
├── src/
│   ├── agent.py              # Main agent wrapper
│   ├── chatbot.py            # Interactive CLI interface
│   ├── config.py             # Configuration management
│   ├── contract_interface.py # Smart contract interface
│   ├── initialize_agent.py   # Agent initialization
│   ├── market_actions.py     # Market-specific tools
│   ├── price_oracle.py       # Price oracle integration
│   └── setup.py              # Setup utilities
├── tests/
│   ├── test_agent.py         # Agent tests
│   ├── test_config.py        # Config tests
│   └── test_market_actions.py # Market action tests
├── requirements.txt          # Python dependencies
└── pyproject.toml           # Project configuration
```

## Available Tools

The agent has access to:

### CDP AgentKit Tools
- Wallet operations (balance, transfer, etc.)
- Token operations (ERC20, WETH, etc.)
- Faucet requests for testnet funds
- Price feeds via Pyth oracle

### Custom Market Tools
- `create_market` - Create new prediction markets
- `place_bet` - Place bets on markets (UP/DOWN)
- `get_market_info` - Query market details
- `claim_winnings` - Claim winnings from resolved markets

## Configuration Options

### LLM Providers

**GLM-4.6 (Default):**
```bash
LLM_PROVIDER=glm
GLM_API_KEY=your-z-ai-api-key
MODEL=glm-4.6
BASE_URL=https://api.z.ai/api/paas/v4/
```

**OpenAI:**
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=your-openai-api-key
MODEL=gpt-4
```

### Network Configuration

**Base Sepolia (Testnet - Default):**
```bash
NETWORK_ID=base-sepolia
BASE_SEPOLIA_RPC_URL=https://sepolia.base.org
```

## Troubleshooting

### Common Issues

**1. "Missing required environment variables"**
- Ensure all required variables are set in `.env`
- Check `.env` is in the `agent/` directory
- Verify no typos in variable names

**2. "Failed to initialize CDP wallet"**
- Verify CDP API credentials are correct
- Ensure `CDP_WALLET_SECRET` is generated from CDP dashboard
- Check network connectivity

**3. "Contract address not set"**
- Deploy contract first: `cd ../contracts && npx hardhat run scripts/deploy.js --network baseSepolia`
- Copy deployed address to `.env`
- Or leave empty to use agent without contract features

**4. "GLM API connection issues"**
- Verify `GLM_API_KEY` is correct
- Check `BASE_URL` is set to `https://api.z.ai/api/paas/v4/`
- Try switching to OpenAI: `LLM_PROVIDER=openai`

**5. Import errors**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again
- Check Python version is 3.11+

## Development

### Code Style
- Modular, Pythonic code
- Type hints for better IDE support
- Clean code principles
- Comprehensive error handling

### Adding New Tools

1. Define tool in `market_actions.py` or create new action provider
2. Add tool to `get_tools()` method
3. Write tests in `tests/`
4. Update documentation

## Notes

- Tools come from CDP AgentKit core plus custom tools for the PredictionMarket contract
- Contract must be compiled (`cd ../contracts && npx hardhat compile`) for ABI availability
- Use testnet (Base Sepolia) for development - no real money involved
- Request free testnet ETH from faucets before testing

## Resources

- [CDP AgentKit Documentation](https://github.com/coinbase/agentkit)
- [LangChain Documentation](https://python.langchain.com/)
- [Base Sepolia Faucet](https://faucet.quicknode.com/base/sepolia)
- [Base Sepolia Explorer](https://sepolia.basescan.org/)

## License

MIT
