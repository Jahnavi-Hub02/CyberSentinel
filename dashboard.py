#!/usr/bin/env python
"""Compatibility shim: run the Streamlit frontend with `python dashboard.py`"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
FRONTEND = ROOT / "frontend" / "app.py"

if __name__ == "__main__":
    if not FRONTEND.exists():
        print("Frontend app not found: frontend/app.py")
        sys.exit(1)
    cmd = [sys.executable, "-m", "streamlit", "run", str(FRONTEND)]
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        pass
