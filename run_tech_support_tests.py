#!/usr/bin/env python3
"""
Run the TechSupportTool tests with proper path configuration.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Now run the pytest command
if __name__ == "__main__":
    import pytest
    pytest.main(["tests/data_generator/test_tech_support.py", "-v"])