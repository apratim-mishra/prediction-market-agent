"""FastAPI REST API for Prediction Market Agent."""
import asyncio
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from config import config
from setup import setup_async
from price_oracle import PriceOracle


# Global state
agent_executor = None
agent_config = None
wallet_provider = None
price_oracle = PriceOracle()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize agent on startup."""
    global agent_executor, agent_config, wallet_provider
    try:
        agent_executor, agent_config, wallet_provider = await setup_async()
        print("✅ Agent initialized successfully")
    except Exception as e:
        print(f"⚠️ Agent initialization failed: {e}")
        print("API will run with limited functionality")
    yield


app = FastAPI(
    title="Prediction Market Agent API",
    description="REST API for the AI-powered prediction market agent",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class ChatRequest(BaseModel):
    message: str = Field(..., description="Message to send to the agent")


class ChatResponse(BaseModel):
    response: str
    success: bool = True


class CreateMarketRequest(BaseModel):
    symbol: str = Field(..., description="Asset symbol (e.g., BTC, ETH, TSLA)")
    target_price: float = Field(..., description="Target price in USD")
    duration_hours: int = Field(..., ge=1, le=168, description="Duration in hours (1-168)")


class PlaceBetRequest(BaseModel):
    market_id: int = Field(..., ge=0, description="Market ID")
    prediction: str = Field(..., description="UP or DOWN")
    amount_eth: float = Field(..., gt=0, description="Amount in ETH")


class MarketInfo(BaseModel):
    market_id: int
    symbol: str
    target_price: float
    total_up_bets: float
    total_down_bets: float
    resolved: bool
    outcome: Optional[str]
    final_price: Optional[float]


class WalletInfo(BaseModel):
    address: str
    network: str
    balance: Optional[str] = None


class PriceResponse(BaseModel):
    symbol: str
    price: float
    source: str


class HealthResponse(BaseModel):
    status: str
    agent_ready: bool
    network: str


# Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API and agent health."""
    return HealthResponse(
        status="healthy",
        agent_ready=agent_executor is not None,
        network=config.network_id,
    )


@app.get("/wallet", response_model=WalletInfo)
async def get_wallet_info():
    """Get wallet address and network info."""
    if not wallet_provider:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        address = wallet_provider.get_address()
        return WalletInfo(
            address=address,
            network=config.network_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message to the agent and get a response."""
    if not agent_executor:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        from langchain_core.messages import HumanMessage
        
        result = await agent_executor.ainvoke(
            {"messages": [HumanMessage(content=request.message)]},
            agent_config
        )
        
        if isinstance(result, dict) and "messages" in result:
            response_text = result["messages"][-1].content
        else:
            response_text = str(result)
        
        return ChatResponse(response=response_text)
    except Exception as e:
        return ChatResponse(response=f"Error: {str(e)}", success=False)


@app.get("/price/{symbol}", response_model=PriceResponse)
async def get_price(symbol: str):
    """Get current price for a symbol."""
    try:
        price = await price_oracle.get_price(symbol.upper())
        return PriceResponse(
            symbol=symbol.upper(),
            price=price,
            source="oracle"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/market/create", response_model=ChatResponse)
async def create_market(request: CreateMarketRequest):
    """Create a new prediction market."""
    if not agent_executor:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    message = (
        f"Create a prediction market for {request.symbol} "
        f"with target price ${request.target_price} "
        f"for {request.duration_hours} hours"
    )
    
    return await chat(ChatRequest(message=message))


@app.post("/market/bet", response_model=ChatResponse)
async def place_bet(request: PlaceBetRequest):
    """Place a bet on a market."""
    if not agent_executor:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    message = (
        f"Place a {request.amount_eth} ETH bet on market {request.market_id} "
        f"predicting {request.prediction.upper()}"
    )
    
    return await chat(ChatRequest(message=message))


@app.get("/market/{market_id}", response_model=ChatResponse)
async def get_market(market_id: int):
    """Get market information."""
    if not agent_executor:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    message = f"Get info for market {market_id}"
    return await chat(ChatRequest(message=message))


@app.post("/market/{market_id}/claim", response_model=ChatResponse)
async def claim_winnings(market_id: int):
    """Claim winnings from a resolved market."""
    if not agent_executor:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    message = f"Claim winnings from market {market_id}"
    return await chat(ChatRequest(message=message))


@app.post("/faucet", response_model=ChatResponse)
async def request_faucet():
    """Request testnet funds from faucet."""
    if not agent_executor:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    message = "Request testnet funds from the faucet"
    return await chat(ChatRequest(message=message))


def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the API server."""
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()

