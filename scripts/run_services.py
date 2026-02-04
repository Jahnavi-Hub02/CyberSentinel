"""Top-level runner for CyberSentinel

Usage:
    python scripts/run_services.py         # starts backend (uvicorn) and frontend (streamlit)
    python scripts/run_services.py backend # start backend only
    python scripts/run_services.py frontend # start frontend only

This script runs both processes as subprocesses and ensures they are terminated on Ctrl+C.
"""
from __future__ import annotations
import os
import sys
import subprocess
from typing import List

API_URL = os.getenv("API_URL", "http://localhost:8000")


def run_backend() -> subprocess.Popen:
    print("Starting backend (uvicorn) on http://127.0.0.1:8000 ...")
    # Use python -m uvicorn so it works in virtual envs even if uvicorn isn't on PATH
    cmd = [sys.executable, "-m", "uvicorn", "backend.app:app", "--host", "127.0.0.1", "--port", "8000"]
    return subprocess.Popen(cmd)


def run_frontend() -> subprocess.Popen:
    print("Starting frontend (streamlit) on http://localhost:8501 ...")
    # Ensure Streamlit uses our API_URL
    env = os.environ.copy()
    env["API_URL"] = API_URL
    cmd = [sys.executable, "-m", "streamlit", "run", "frontend/app.py", "--server.port", "8501", "--server.headless", "true"]
    return subprocess.Popen(cmd, env=env)


def main(argv: List[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    mode = "both"
    if argv:
        mode = argv[0].lower()
    procs = []
    try:
        if mode in ("both", "backend"):
            p = run_backend()
            procs.append(p)
        if mode in ("both", "frontend"):
            p2 = run_frontend()
            procs.append(p2)
        # Wait until interrupted
        print("Press Ctrl+C to stop all services.")
        for p in procs:
            p.wait()
    except KeyboardInterrupt:
        print("Shutting down services...")
        for p in procs:
            try:
                p.terminate()
            except Exception:
                pass
    finally:
        for p in procs:
            if p.poll() is None:
                try:
                    p.kill()
                except Exception:
                    pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
