#!/usr/bin/env python3
"""Token and Context Size Audit CLI Tool for AdaptPulse."""
import sys
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from intervals_plan.token_audit import main

if __name__ == "__main__":
    main()
