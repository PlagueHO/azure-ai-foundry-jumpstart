"""
Configure pytest for data_generator.tools tests.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parents[3] / "src"))