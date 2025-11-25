"""Health check for the prediction market agent environment.

Usage:
    cd agent && python src/health_check.py
"""
import importlib
import sys
from typing import Dict

from config import config


def _try_import(module: str) -> tuple[bool, str]:
    """Try to import a module and return status."""
    try:
        mod = importlib.import_module(module)
        version = getattr(mod, "__version__", "installed")
        return True, version
    except ImportError as e:
        return False, str(e)


def check_dependencies() -> Dict[str, tuple[bool, str]]:
    """Check all required dependencies."""
    modules = {
        "coinbase_agentkit": "coinbase_agentkit",
        "coinbase_agentkit_langchain": "coinbase_agentkit_langchain",
        "langchain": "langchain",
        "langchain_openai": "langchain_openai",
        "langgraph": "langgraph",
        "openai": "openai",
        "web3": "web3",
        "aiohttp": "aiohttp",
        "pydantic": "pydantic",
    }
    
    results = {}
    for label, module in modules.items():
        results[label] = _try_import(module)
    return results


def check_env_vars() -> Dict[str, bool]:
    """Check required environment variables."""
    checks = {
        "CDP_API_KEY_NAME": bool(config.cdp_api_key_name),
        "CDP_API_PRIVATE_KEY": bool(config.cdp_private_key),
        "CDP_WALLET_SECRET": bool(config.cdp_wallet_secret),
        "LLM_API_KEY (GLM or OpenAI)": bool(config.glm_api_key or config.openai_api_key),
        "CONTRACT_ADDRESS": config.has_valid_contract,
        "BASE_SEPOLIA_RPC_URL": bool(config.base_sepolia_rpc_url),
    }
    return checks


def main() -> int:
    """Run health check and return exit code."""
    print("=" * 50)
    print("Prediction Market Agent - Health Check")
    print("=" * 50)
    
    print("\n📦 Dependency Check")
    print("-" * 30)
    dep_results = check_dependencies()
    dep_failures = []
    
    for name, (ok, info) in dep_results.items():
        status = "✅" if ok else "❌"
        print(f"  {status} {name:30} {info}")
        if not ok:
            dep_failures.append(name)
    
    print("\n🔑 Environment Variables")
    print("-" * 30)
    env_results = check_env_vars()
    env_missing = []
    
    for name, ok in env_results.items():
        status = "✅" if ok else "⚠️ " if "optional" in name.lower() else "❌"
        state = "set" if ok else "missing"
        print(f"  {status} {name:30} {state}")
        if not ok and "optional" not in name.lower():
            env_missing.append(name)
    
    print("\n📋 Summary")
    print("-" * 30)
    
    if dep_failures:
        print(f"  ❌ Missing dependencies: {', '.join(dep_failures)}")
        print("     Run: pip install -r requirements.txt")
    
    if env_missing:
        print(f"  ❌ Missing env vars: {', '.join(env_missing)}")
        print("     Copy .env.example to .env and fill in values")
    
    if not dep_failures and not env_missing:
        print("  ✅ All checks passed! Ready to run.")
        return 0
    
    return 1


if __name__ == "__main__":
    sys.exit(main())
