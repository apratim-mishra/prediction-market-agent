# Prediction Market Contracts

Hardhat project for the `PredictionMarket` contract targeting Base Sepolia.

## Setup

1. Install deps:
   ```sh
   npm install
   ```
2. Create `.env` (copy from repo root `.env.example`) and fill:
   - `PRIVATE_KEY` (Base Sepolia funded EOA)
   - `BASE_SEPOLIA_RPC_URL` (Alchemy recommended)
   - `BASESCAN_API_KEY` (optional, for verification)

## Commands

- Compile ABI (needed by the agent):  
  `npx hardhat compile`
- Deploy to Base Sepolia with an initial market:  
  `npx hardhat run scripts/deploy.js --network baseSepolia`
- Verify (optional):  
  `npx hardhat verify --network baseSepolia <deployed_address>`

Deployments are written to `contracts/deployed.json` and logs show the contract address to paste into `agent/.env`.
