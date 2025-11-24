# tests/__init__.py
"""
Test package for the prediction market agent.

This package contains tests for all components of the prediction market agent,
including configuration, agent initialization, and market actions.

All tests in this package automatically load environment variables from .env files
to ensure consistent testing across different environments.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
test_dir = Path(__file__).parent
src_dir = test_dir.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Load environment variables from .env file if it exists
from dotenv import load_dotenv

# Try to load .env from multiple locations
env_files = [
    test_dir.parent / ".env",
    test_dir.parent / ".env.local",
    test_dir.parent / ".env.test",
]

for env_file in env_files:
    if env_file.exists():
        load_dotenv(env_file)