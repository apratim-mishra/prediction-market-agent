"""Smart contract interface for Prediction Market."""
import asyncio
import json
from pathlib import Path
from typing import Any, Optional

from coinbase_agentkit import AgentKit
from web3 import Web3


class PredictionMarketContract:
    """Interface to interact with the Prediction Market smart contract."""
    
    def __init__(
        self,
        agent_kit: AgentKit,
        contract_address: Optional[str] = None,
        rpc_url: Optional[str] = None
    ):
        self.agent_kit = agent_kit
        self.contract_address = self._validate_address(contract_address)
        self.abi = self._load_abi()
        self.web3 = self._init_web3(rpc_url)
        self.contract = self._init_contract()
    
    def _validate_address(self, address: Optional[str]) -> Optional[str]:
        """Validate and checksum the contract address."""
        if not address:
            return None
        
        invalid_patterns = ["...", "your_", "placeholder"]
        if any(p in address.lower() for p in invalid_patterns):
            raise ValueError(f"Invalid contract address: '{address}'. Deploy the contract first.")
        
        try:
            return Web3.to_checksum_address(address)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid Ethereum address format: {address}") from e
    
    def _load_abi(self) -> list:
        """Load contract ABI from Hardhat artifacts."""
        artifacts_path = (
            Path(__file__).resolve().parents[2]
            / "contracts" / "artifacts" / "contracts"
            / "PredictionMarket.sol" / "PredictionMarket.json"
        )
        if not artifacts_path.exists():
            raise FileNotFoundError(
                f"ABI not found at {artifacts_path}. "
                "Run `cd contracts && npx hardhat compile` first."
            )
        with artifacts_path.open() as f:
            return json.load(f)["abi"]
    
    def _init_web3(self, rpc_url: Optional[str]) -> Optional[Web3]:
        """Initialize Web3 connection."""
        if not rpc_url:
            return None
        web3 = Web3(Web3.HTTPProvider(rpc_url))
        if not web3.is_connected():
            raise ValueError(f"Unable to connect to RPC at {rpc_url}")
        return web3
    
    def _init_contract(self):
        """Initialize contract instance if web3 and address are available."""
        if self.web3 and self.contract_address:
            return self.web3.eth.contract(address=self.contract_address, abi=self.abi)
        return None
    
    def _ensure_contract_address(self) -> None:
        """Raise an error if contract address is not set."""
        if not self.contract_address:
            raise ValueError("Contract address not set. Deploy the contract first.")
    
    async def _invoke_contract(
        self,
        function_name: str,
        args: list,
        value: Optional[int] = None
    ) -> dict[str, Any]:
        """Invoke a contract function through AgentKit."""
        self._ensure_contract_address()
        
        invoke_method = getattr(self.agent_kit, "invoke_contract", None)
        if invoke_method is None:
            invoke_method = getattr(self.agent_kit, "transact_contract", None)
        
        if invoke_method is None:
            raise AttributeError("AgentKit instance does not support contract invocation")
        
        return await invoke_method(
            contract_address=self.contract_address,
            abi=self.abi,
            function_name=function_name,
            args=args,
            value=value,
        )
    
    async def _read_contract(self, function_name: str, args: list) -> Any:
        """Read contract state through AgentKit."""
        self._ensure_contract_address()
        
        read_method = getattr(self.agent_kit, "read_contract", None)
        if read_method is None:
            read_method = getattr(self.agent_kit, "call_contract", None)
        
        if read_method is None:
            raise AttributeError("AgentKit instance does not support contract reads")
        
        return await read_method(
            contract_address=self.contract_address,
            abi=self.abi,
            function_name=function_name,
            args=args,
        )
    
    async def create_market(
        self,
        symbol: str,
        target_price: int,
        duration_hours: int
    ) -> dict[str, Any]:
        """Create a new prediction market."""
        result = await self._invoke_contract(
            "createMarket",
            [symbol, target_price, duration_hours]
        )
        return {
            "market_id": result.get("marketId") or result.get("result"),
            "tx_hash": result.get("transactionHash")
        }
    
    async def place_bet(
        self,
        market_id: int,
        prediction: bool,
        amount_eth: float
    ) -> dict[str, Any]:
        """Place a bet on a market."""
        amount_wei = Web3.to_wei(amount_eth, "ether")
        result = await self._invoke_contract(
            "placeBet",
            [market_id, prediction],
            value=amount_wei
        )
        return {
            "success": True,
            "tx_hash": result.get("transactionHash"),
            "market_id": market_id,
            "prediction": "UP" if prediction else "DOWN",
            "amount": amount_eth,
        }
    
    async def resolve_market(
        self,
        market_id: int,
        final_price: int
    ) -> dict[str, Any]:
        """Resolve a market with the final price."""
        result = await self._invoke_contract(
            "resolveMarket",
            [market_id, final_price]
        )
        return {
            "market_id": market_id,
            "final_price": final_price,
            "tx_hash": result.get("transactionHash")
        }
    
    async def claim_winnings(self, market_id: int) -> dict[str, Any]:
        """Claim winnings from a resolved market."""
        result = await self._invoke_contract("claimWinnings", [market_id])
        return {
            "market_id": market_id,
            "tx_hash": result.get("transactionHash")
        }
    
    async def get_market_info(self, market_id: int) -> dict[str, Any]:
        """Get information about a specific market."""
        self._ensure_contract_address()
        
        if self.contract:
            result = await asyncio.to_thread(
                self.contract.functions.getMarketInfo(market_id).call
            )
        else:
            result = await self._read_contract("getMarketInfo", [market_id])
        
        return {
            "symbol": result[0],
            "target_price": result[1] / 100,
            "deadline": result[2],
            "total_up_bets": float(Web3.from_wei(result[3], "ether")),
            "total_down_bets": float(Web3.from_wei(result[4], "ether")),
            "resolved": result[5],
            "outcome": "UP" if result[6] else "DOWN" if result[5] else None,
            "final_price": result[7] / 100 if result[7] > 0 else None,
        }
