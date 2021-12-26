"""Initialize a test."""

import os
import sys


def setup():
    """Configure environment for testing."""
    root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    print(f"Add directory {root} to sys.path")
    sys.path.append(str(root))
