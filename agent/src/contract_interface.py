# src/contract_interface.py

"""Smart contract interface for Prediction Market"""
import asyncio
import json
from pathlib import Path
from typing import Any, Dict, Optional

from coinbase_agentkit import AgentKit
from web3 import Web3


class PredictionMarketContract:
    """Interface to interact with the Prediction Market smart contract"""

    def __init__(self, agent_kit: AgentKit, contract_address: Optional[str] = None, rpc_url: Optional[str] = None):
        self.agent_kit = agent_kit
        
        # Validate and set contract address
        if contract_address:
            # Check for placeholder values
            if "..." in contract_address or "your_" in contract_address.lower() or "placeholder" in contract_address.lower():
                raise ValueError(
                    f"Invalid contract address: '{contract_address}'. "
                    "Please deploy the contract first and set CONTRACT_ADDRESS in .env"
                )
            try:
                self.contract_address = Web3.to_checksum_address(contract_address)
            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid Ethereum address format: {contract_address}") from e
        else:
            self.contract_address = None
        
        self.abi = self._load_abi()
        self.web3 = Web3(Web3.HTTPProvider(rpc_url)) if rpc_url else None
        if self.web3 and not self.web3.is_connected():
            raise ValueError(f"Unable to connect to RPC at {rpc_url}")
        
        self.contract = (
            self.web3.eth.contract(address=self.contract_address, abi=self.abi) 
            if self.web3 and self.contract_address else None
        )

    def _load_abi(self) -> list:
        """Load contract ABI from Hardhat artifacts"""
        artifacts_path = (
            Path(__file__).resolve().parents[2]
            / "contracts"
            / "artifacts"
            / "contracts"
            / "PredictionMarket.sol"
            / "PredictionMarket.json"
        )
        if not artifacts_path.exists():
            raise FileNotFoundError(
                f"ABI not found at {artifacts_path}. Run `cd contracts && npx hardhat compile` first."
            )
        with artifacts_path.open() as f:
            return json.load(f)["abi"]

    async def _invoke_contract(self, function_name: str, args: list, value: int | None = None):
        """Wrapper to handle slight API differences between AgentKit versions."""
        if not self.contract_address:
            raise ValueError("Contract address not set. Deploy the contract first.")
        
        if hasattr(self.agent_kit, "invoke_contract"):
            return await self.agent_kit.invoke_contract(
                contract_address=self.contract_address,
                abi=self.abi,
                function_name=function_name,
                args=args,
                value=value,
            )
        if hasattr(self.agent_kit, "transact_contract"):
            return await self.agent_kit.transact_contract(
                contract_address=self.contract_address,
                abi=self.abi,
                function_name=function_name,
                args=args,
                value=value,
            )
        raise AttributeError("AgentKit instance does not support contract invocation")

    async def _read_contract(self, function_name: str, args: list):
        """Wrapper to read contract state via AgentKit."""
        if not self.contract_address:
            raise ValueError("Contract address not set. Deploy the contract first.")
        
        if hasattr(self.agent_kit, "read_contract"):
            return await self.agent_kit.read_contract(
                contract_address=self.contract_address,
                abi=self.abi,
                function_name=function_name,
                args=args,
            )
        if hasattr(self.agent_kit, "call_contract"):
            return await self.agent_kit.call_contract(
                contract_address=self.contract_address,
                abi=self.abi,
                function_name=function_name,
                args=args,
            )
        raise AttributeError("AgentKit instance does not support contract reads")

    async def create_market(self, symbol: str, target_price: int, duration_hours: int) -> Dict[str, Any]:
        """Create a new prediction market"""
        result = await self._invoke_contract("createMarket", [symbol, target_price, duration_hours])
        return {"market_id": result.get("marketId") or result.get("result"), "tx_hash": result.get("transactionHash")}

    async def place_bet(self, market_id: int, prediction: bool, amount_eth: float) -> Dict[str, Any]:
        """Place a bet on a market"""
        amount_wei = Web3.to_wei(amount_eth, "ether")
        result = await self._invoke_contract("placeBet", [market_id, prediction], value=amount_wei)
        return {
            "success": True,
            "tx_hash": result.get("transactionHash"),
            "market_id": market_id,
            "prediction": "UP" if prediction else "DOWN",
            "amount": amount_eth,
        }

    async def resolve_market(self, market_id: int, final_price: int) -> Dict[str, Any]:
        """Resolve a market with the final price"""
        result = await self._invoke_contract("resolveMarket", [market_id, final_price])
        return {"market_id": market_id, "final_price": final_price, "tx_hash": result.get("transactionHash")}

    async def claim_winnings(self, market_id: int) -> Dict[str, Any]:
        """Claim winnings from a resolved market"""
        result = await self._invoke_contract("claimWinnings", [market_id])
        return {"market_id": market_id, "tx_hash": result.get("transactionHash")}

    async def get_market_info(self, market_id: int) -> Dict[str, Any]:
        """Get information about a specific market"""
        if not self.contract_address:
            raise ValueError("Contract address not set. Deploy the contract first.")
        
        if self.contract:
            result = await asyncio.to_thread(self.contract.functions.getMarketInfo(market_id).call)
        else:
            result = await self._read_contract("getMarketInfo", [market_id])

        return {
            "symbol": result[0],
            "target_price": result[1] / 100,  # Convert from cents to dollars
            "deadline": result[2],
            "total_up_bets": Web3.from_wei(result[3], "ether"),
            "total_down_bets": Web3.from_wei(result[4], "ether"),
            "resolved": result[5],
            "outcome": "UP" if result[6] else "DOWN" if result[5] else None,
            "final_price": result[7] / 100 if result[7] > 0 else None,
        }