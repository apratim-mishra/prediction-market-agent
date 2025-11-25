# Deployment Guide

## Prerequisites

- Node.js 18+
- Python 3.11+
- Base Sepolia testnet ETH

## Smart Contract Deployment

### 1. Setup Hardhat

```bash
cd contracts
npm install
```

### 2. Configure Network

Update `hardhat.config.js` with your RPC URL:

```javascript
module.exports = {
  networks: {
    baseSepolia: {
      url: process.env.BASE_SEPOLIA_RPC_URL || "https://sepolia.base.org",
      accounts: [process.env.DEPLOYER_PRIVATE_KEY]
    }
  }
};
```

### 3. Deploy

```bash
# Set deployer private key
export DEPLOYER_PRIVATE_KEY=your_private_key

# Deploy to Base Sepolia
npx hardhat run scripts/deploy.js --network baseSepolia
```

### 4. Verify Contract (Optional)

```bash
npx hardhat verify --network baseSepolia <CONTRACT_ADDRESS>
```

### 5. Update Configuration

Add the deployed contract address to your `.env`:

```bash
CONTRACT_ADDRESS=0x...your_deployed_address
```

## Agent Deployment

### Development

```bash
cd agent
source ../.venv/bin/activate
python src/chatbot.py
```

### Production

Consider using:
- **Docker** for containerization
- **Systemd** for service management
- **PM2** for process management

Example systemd service:

```ini
[Unit]
Description=Prediction Market Agent
After=network.target

[Service]
Type=simple
User=agent
WorkingDirectory=/opt/prediction-market-agent/agent
Environment="PATH=/opt/prediction-market-agent/.venv/bin"
ExecStart=/opt/prediction-market-agent/.venv/bin/python src/chatbot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## Getting Testnet ETH

### Base Sepolia Faucets

1. **Coinbase Faucet** - Use the agent to request:
   ```
   > Request testnet funds from the faucet
   ```

2. **Base Sepolia Faucet** - https://www.coinbase.com/faucets/base-ethereum-goerli-faucet

3. **Alchemy Faucet** - https://sepoliafaucet.com/

## Health Check

After deployment, verify everything works:

```bash
python src/health_check.py
```

Expected output:
```
==================================================
Prediction Market Agent - Health Check
==================================================

📦 Dependency Check
------------------------------
  ✅ coinbase_agentkit           installed
  ✅ langchain                   installed
  ...

🔑 Environment Variables
------------------------------
  ✅ CDP_API_KEY_NAME            set
  ✅ CDP_API_PRIVATE_KEY         set
  ✅ CDP_WALLET_SECRET           set
  ✅ LLM_API_KEY                 set
  ✅ CONTRACT_ADDRESS            set

📋 Summary
------------------------------
  ✅ All checks passed! Ready to run.
```

## Monitoring

### Logs

Monitor agent output for:
- Transaction hashes
- Error messages
- API rate limits

### Blockchain Explorer

Track transactions on [Base Sepolia Explorer](https://sepolia.basescan.org/)

### Contract Events

Key events to monitor:
- `MarketCreated` - New market created
- `BetPlaced` - Bet placed on market
- `MarketResolved` - Market resolved with outcome
- `WinningsClaimed` - User claimed winnings

