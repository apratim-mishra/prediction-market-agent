# Architecture Documentation

## Overview

The Prediction Market Agent is a multi-component system that combines AI capabilities with blockchain interactions.

## Components

### 1. Agent Layer (`agent/src/`)

#### `agent.py`
- Main `PredictionMarketAgent` class
- Programmatic interface for the agent
- Async/await support for all operations

#### `chatbot.py`
- Interactive command-line interface
- Chat mode for user interactions
- Autonomous mode for periodic actions

#### `config.py`
- Centralized configuration management
- Environment variable loading with fallbacks
- Validation helpers

#### `initialize_agent.py`
- AgentKit initialization
- LLM configuration (GLM/OpenAI)
- Tool registration

### 2. Market Interface (`agent/src/`)

#### `contract_interface.py`
- Low-level contract interactions
- ABI loading and validation
- Web3 integration

#### `market_actions.py`
- LangChain tool definitions
- Input schema validation with Pydantic
- User-friendly response formatting

### 3. Price Oracle (`agent/src/price_oracle.py`)

Multi-source price data:
- **CoinGecko** - Crypto prices
- **Coinbase** - Crypto prices (no API key required)
- **Alpha Vantage** - Stock prices
- **Polygon** - Stock/Crypto prices

### 4. Smart Contracts (`contracts/`)

#### `PredictionMarket.sol`
- OpenZeppelin base (Ownable, ReentrancyGuard)
- Market creation and management
- Betting and settlement logic

## Data Flow

```
User Input
    │
    ▼
┌─────────────┐     ┌──────────────┐
│   Chatbot   │────►│   AgentKit   │
└─────────────┘     └──────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   LangChain  │
                    │    Agent     │
                    └──────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌────────────┐  ┌────────────┐  ┌────────────┐
    │   Wallet   │  │   Market   │  │   Price    │
    │   Actions  │  │   Actions  │  │   Oracle   │
    └────────────┘  └────────────┘  └────────────┘
           │               │
           ▼               ▼
    ┌─────────────────────────────┐
    │      Base Sepolia           │
    │      (Smart Contract)       │
    └─────────────────────────────┘
```

## Security Considerations

1. **API Key Management** - All keys stored in `.env`, never committed
2. **Contract Security** - ReentrancyGuard, Ownable access control
3. **Input Validation** - Pydantic schemas for all user inputs
4. **Error Handling** - Graceful failures with informative messages

## Extensibility

### Adding New Price Sources

1. Add source to `PriceSource` enum
2. Add endpoint to `ENDPOINTS` dict
3. Implement `_fetch_<source>()` method
4. Update `get_price()` routing logic

### Adding New Market Actions

1. Create input schema in `market_actions.py`
2. Add async implementation method
3. Register tool in `get_tools()`
4. Update contract interface if needed

### Adding New LLM Providers

1. Add provider check in `_create_llm()`
2. Configure in `.env.example`
3. Update config validation

