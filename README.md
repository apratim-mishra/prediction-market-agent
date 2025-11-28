# 🎯 Prediction Market Agent

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Base Sepolia](https://img.shields.io/badge/Network-Base%20Sepolia-blue)](https://docs.base.org/)
[![Solidity](https://img.shields.io/badge/Solidity-0.8.24-363636.svg)](https://soliditylang.org/)

An AI-powered prediction market agent built with **Coinbase AgentKit** for the **Base Sepolia** testnet. Create markets, place bets, and interact with smart contracts through natural language.

<p align="center">
  <img src="https://img.shields.io/badge/Powered%20by-Coinbase%20AgentKit-0052FF?style=for-the-badge&logo=coinbase" alt="Coinbase AgentKit">
</p>

---

## ✨ Features

| Feature                  | Description                                                 |
| ------------------------ | ----------------------------------------------------------- |
| 🤖 **AI Agent**          | Natural language interface powered by LangChain & LangGraph |
| 🔗 **Smart Contracts**   | Full prediction market on Base Sepolia                      |
| 💰 **CDP Wallet**        | Seamless Coinbase Developer Platform integration            |
| 📊 **Price Oracle**      | Real-time prices from CoinGecko, Coinbase, Pyth Network     |
| 🎯 **Market Operations** | Create markets, bet UP/DOWN, claim winnings                 |
| 🌐 **Multi-LLM**         | Supports OpenAI GPT-4 and GLM-4.6                           |
| 🧪 **Testnet Ready**     | Pre-configured for Base Sepolia with faucet integration     |

---

## 🏗️ Architecture

```
prediction-market-agent/
├── agent/                      # Python agent + API
│   ├── src/
│   │   ├── agent.py            # Main agent class
│   │   ├── api.py              # FastAPI REST API
│   │   ├── chatbot.py          # Interactive CLI
│   │   ├── config.py           # Configuration
│   │   ├── contract_interface.py
│   │   ├── market_actions.py   # LangChain tools
│   │   └── price_oracle.py     # Multi-source prices
│   ├── tests/                  # Test suite (26 tests)
│   └── requirements.txt
├── frontend/                   # React + TypeScript UI
│   ├── src/
│   │   ├── App.tsx
│   │   ├── api.ts              # API client
│   │   └── components/         # UI components
│   └── package.json
├── contracts/                  # Solidity contracts
│   ├── contracts/PredictionMarket.sol
│   └── scripts/deploy.js
└── docs/                       # Documentation
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ (for contracts)
- [CDP API Keys](https://portal.cdp.coinbase.com/)
- LLM API Key ([Z.AI](https://z.ai) or [OpenAI](https://platform.openai.com/))

### Installation

```bash
# Clone repository
git clone https://github.com/apratim-mishra/prediction-market-agent.git
cd prediction-market-agent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
cd agent
pip install -r requirements.txt
```

### Configuration

Create `agent/.env` file with your API keys:

```bash
# CDP Configuration (Required) - Get from: https://portal.cdp.coinbase.com/
CDP_API_KEY_NAME=your-key-name
CDP_API_PRIVATE_KEY=your-private-key
CDP_WALLET_SECRET=your-wallet-secret
NETWORK_ID=base-sepolia

# LLM Configuration (Choose one)
LLM_PROVIDER=glm
GLM_API_KEY=your-glm-key
MODEL=glm-4.6
BASE_URL=https://api.z.ai/api/paas/v4/
# OR use OpenAI:
# LLM_PROVIDER=openai
# OPENAI_API_KEY=your-openai-key
# MODEL=gpt-4

# Contract (Optional - set after deployment)
CONTRACT_ADDRESS=0x...
BASE_SEPOLIA_RPC_URL=https://sepolia.base.org
```

### Run

From the `agent/` directory:

```bash
cd agent  # if not already there

# 1. Verify setup (recommended first step)
python src/health_check.py

# 2. Run CLI chatbot (interactive)
python src/chatbot.py

# 3. Or run API server (for frontend)
python src/api.py  # Runs on http://localhost:8000
```

### Frontend (Optional)

```bash
cd frontend
npm install
npm run dev
```

Opens at http://localhost:3000

---

## 💬 Usage Examples

### Web UI

Start the API server and frontend:

```bash
# Terminal 1: Backend
cd agent && python src/api.py

# Terminal 2: Frontend
cd frontend && npm run dev
```

Access at http://localhost:3000

### Chat Mode (CLI)

```
> What is my wallet address?
> What is my wallet balance?
> Request testnet funds from the faucet
> What's the current price of BTC?
> Get info for market 0
> Place a 0.0001 ETH bet on market 0 predicting UP
> Place a 0.0001 ETH bet on market 0 predicting DOWN
> Claim winnings from market 0
```

**Note:** Creating markets requires contract ownership. Use Hardhat to create markets.

### Programmatic

```python
import asyncio
from agent import PredictionMarketAgent

async def main():
    agent = PredictionMarketAgent()
    await agent.initialize()

    response = await agent.run("What is my wallet address?")
    print(response)

asyncio.run(main())
```

---

## 📜 Smart Contract

**PredictionMarket.sol** on Base Sepolia:

| Function                                      | Description                   |
| --------------------------------------------- | ----------------------------- |
| `createMarket(symbol, targetPrice, duration)` | Create new market             |
| `placeBet(marketId, prediction)`              | Bet UP (true) or DOWN (false) |
| `resolveMarket(marketId, finalPrice)`         | Resolve with final price      |
| `claimWinnings(marketId)`                     | Claim winnings                |

**Parameters:**

- Min bet: 0.00001 ETH (configurable in contract)
- Platform fee: 2%
- Max duration: 168 hours (1 week)

### Deploy Contract

```bash
cd contracts
npm install --legacy-peer-deps
npx hardhat compile
npx hardhat run scripts/deploy.js --network baseSepolia
```

**After deployment:**
1. Copy the deployed contract address from the output
2. Update `agent/.env` with `CONTRACT_ADDRESS=0x...`
3. Restart the agent

### Create Markets (via Hardhat)

Only the contract owner can create markets. Use Hardhat console:

```bash
cd contracts
npx hardhat console --network baseSepolia
```

```javascript
const c = await ethers.getContractAt("PredictionMarket", "YOUR_CONTRACT_ADDRESS");
await c.createMarket("BTC", 9500000, 24);  // BTC at $95,000 for 24 hours
await c.createMarket("ETH", 400000, 48);   // ETH at $4,000 for 48 hours
```

---

## 🧪 Testing

```bash
cd agent

# Run all tests
pytest -v

# With coverage
pytest --cov=src --cov-report=html
```

**26 tests** covering config, market actions, and agent initialization.

---

## 🔧 API Keys

| Service       | Get Keys At                                                 | Required |
| ------------- | ----------------------------------------------------------- | -------- |
| CDP           | [portal.cdp.coinbase.com](https://portal.cdp.coinbase.com/) | ✅       |
| GLM (Z.AI)    | [z.ai](https://z.ai)                                        | ✅\*     |
| OpenAI        | [platform.openai.com](https://platform.openai.com/)         | ✅\*     |
| Alpha Vantage | [alphavantage.co](https://www.alphavantage.co/)             | Optional |
| CoinGecko     | [coingecko.com](https://www.coingecko.com/)                 | Optional |

\*One of GLM or OpenAI required.

---

## 🐛 Troubleshooting

| Issue                       | Solution                                                          |
| --------------------------- | ----------------------------------------------------------------- |
| Missing env variables       | Run `python src/health_check.py`                                  |
| CDP wallet error            | Verify credentials at CDP dashboard                               |
| GLM connection failed       | Check BASE_URL: `https://api.z.ai/api/paas/v4/`                   |
| Contract not found          | Deploy contract or remove CONTRACT_ADDRESS                        |
| "Unable to estimate gas"    | Wallet needs more ETH, or bet amount below minimum                |
| npm install fails           | Use `npm install --legacy-peer-deps`                              |
| Market tools not available  | Ensure CONTRACT_ADDRESS is set correctly in .env                  |
| "Only owner" error          | Only deployer wallet can create markets (use Hardhat)             |
| Wallet has 0 ETH            | Ask agent: "Request testnet funds from the faucet"                |

---

## 📚 Resources

- [Coinbase AgentKit](https://github.com/coinbase/agentkit)
- [CDP Documentation](https://docs.cdp.coinbase.com/)
- [Base Sepolia](https://docs.base.org/network-information)
- [LangChain](https://python.langchain.com/)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

---

<p align="center">
  Built with ❤️ using Coinbase AgentKit
</p>
