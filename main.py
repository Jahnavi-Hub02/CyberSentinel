#!/usr/bin/env python
"""
CyberSentinel - Main Entry Point
Runs backend API and/or frontend dashboard
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path


def get_project_root():
    """Get the project root directory."""
    return Path(__file__).parent


def run_backend(host: str = "127.0.0.1", port: int = 8000, reload: bool = True):
    """Run the FastAPI backend server."""
    os.chdir(get_project_root())
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "backend.main:create_app",
        "--host",
        host,
        "--port",
        str(port),
    ]
    if reload:
        cmd.append("--reload")
    
    print(f"🚀 Starting Backend API on http://{host}:{port}")
    print(f"📚 API Docs available at http://{host}:{port}/docs")
    subprocess.run(cmd)


def run_frontend(port: int = 8501):
    """Run the Streamlit frontend dashboard."""
    os.chdir(get_project_root())
    cmd = [sys.executable, "-m", "streamlit", "run", "app.py", "--logger.level=info"]
    
    print(f"🎨 Starting Frontend Dashboard on http://127.0.0.1:{port}")
    subprocess.run(cmd)


def run_both(backend_port: int = 8000, frontend_port: int = 8501):
    """Run both backend and frontend (requires tmux or screen on Unix)."""
    import platform
    
    print("⚠️  To run both services, use two terminal windows:")
    print(f"\n  Terminal 1: python main.py --backend --port {backend_port}")
    print(f"  Terminal 2: python main.py --frontend --port {frontend_port}")


def main():
    parser = argparse.ArgumentParser(
        description="CyberSentinel - Run backend API and/or frontend dashboard"
    )
    parser.add_argument(
        "--backend",
        action="store_true",
        help="Run backend API server",
    )
    parser.add_argument(
        "--frontend",
        action="store_true",
        help="Run Streamlit frontend dashboard",
    )
    parser.add_argument(
        "--both",
        action="store_true",
        help="Show instructions for running both (requires separate terminals)",
    )
    parser.add_argument(
        "--backend-port",
        type=int,
        default=8000,
        help="Port for backend API (default: 8000)",
    )
    parser.add_argument(
        "--frontend-port",
        type=int,
        default=8501,
        help="Port for frontend dashboard (default: 8501)",
    )
    parser.add_argument(
        "--no-reload",
        action="store_true",
        help="Disable auto-reload for backend",
    )
    
    args = parser.parse_args()
    
    # Default: run frontend if no args
    if not (args.backend or args.frontend or args.both):
        args.frontend = True
    
    if args.backend:
        run_backend(port=args.backend_port, reload=not args.no_reload)
    elif args.frontend:
        run_frontend(port=args.frontend_port)
    elif args.both:
        run_both(args.backend_port, args.frontend_port)


if __name__ == "__main__":
    main()
