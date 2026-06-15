#!/usr/bin/env python3
"""Run market breadth weak-to-strong analysis from a source checkout."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from krast_market_breadth.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
