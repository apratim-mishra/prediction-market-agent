"""Quick health check for the prediction market agent environment.

Run with:
    cd agent && python src/health_check.py
"""

import importlib
import sys
from typing import Dict, Tuple

from config import config


def _try_import(module: str) -> Tuple[bool, str]:
    try:
        mod = importlib.import_module(module)
        version = getattr(mod, "__version__", "unknown")
        return True, version
    except Exception as exc:  # pragma: no cover - diagnostic only
        return False, str(exc)


def main() -> int:
    checks = {
        "coinbase_agentkit": "coinbase_agentkit",
        "coinbase_agentkit_langchain": "coinbase_agentkit_langchain",
        "langchain": "langchain",
        "langchain_openai": "langchain_openai",
        "langgraph": "langgraph",
        "openai": "openai",
        "web3": "web3",
        "aiohttp": "aiohttp",
    }

    print("== Dependency import check ==")
    failures: Dict[str, str] = {}
    for label, module in checks.items():
        ok, info = _try_import(module)
        status = "ok" if ok else "fail"
        print(f"{label:24} {status} ({info})")
        if not ok:
            failures[label] = info

    print("\n== Required env variables ==")
    required = {
        "CDP_API_KEY_NAME": config.cdp_api_key_name,
        "CDP_API_PRIVATE_KEY": config.cdp_private_key,
        "OPENAI_API_KEY": config.openai_api_key,
        "CONTRACT_ADDRESS": config.contract_address,
        "BASE_SEPOLIA_RPC_URL": config.base_sepolia_rpc_url,
    }
    missing = [key for key, val in required.items() if not val]
    for key, val in required.items():
        print(f"{key:24} {'set' if val else 'missing'}")

    if failures:
        print("\nSome imports failed. Install/upgrade with:\n  pip install -r requirements.txt")
    if missing:
        print("\nMissing env vars:", ", ".join(missing))

    return 1 if failures or missing else 0


if __name__ == "__main__":
    sys.exit(main())
