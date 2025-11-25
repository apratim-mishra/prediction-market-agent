# Prediction Market Frontend

React + TypeScript frontend for the Prediction Market Agent.

## Features

- 💰 **Wallet Management** - View address, request faucet funds
- 📊 **Live Prices** - Real-time BTC, ETH, SOL prices
- 🎯 **Create Markets** - Create prediction markets for any asset
- 🎲 **Place Bets** - Bet UP or DOWN on market outcomes
- 📋 **Market Info** - View market details and claim winnings
- 💬 **AI Chat** - Natural language interaction with the agent

## Quick Start

### Prerequisites

- Node.js 18+
- Backend API running on port 8000

### Install

```bash
npm install
```

### Run Development Server

```bash
npm run dev
```

Opens at http://localhost:3000

### Build for Production

```bash
npm run build
npm run preview
```

## Architecture

```
frontend/
├── src/
│   ├── main.tsx           # Entry point
│   ├── App.tsx            # Main app component
│   ├── api.ts             # API client
│   ├── index.css          # Styles
│   └── components/
│       ├── WalletCard.tsx
│       ├── PriceCard.tsx
│       ├── CreateMarketCard.tsx
│       ├── PlaceBetCard.tsx
│       ├── MarketInfoCard.tsx
│       └── ChatCard.tsx
├── package.json
├── vite.config.ts
└── tsconfig.json
```

## API Proxy

The Vite dev server proxies `/api` requests to the backend:

```
Frontend (3000) -> /api/* -> Backend (8000)
```

## Styling

- Dark theme with blue accents (Coinbase-inspired)
- Space Grotesk for headings
- JetBrains Mono for code/prices
- Responsive grid layout

## Development

```bash
# Start frontend
npm run dev

# In another terminal, start backend
cd ../agent
source ../.venv/bin/activate
python src/api.py
```

