"""
Entry point to run Streamlit locally without Docker.
Usage: streamlit run app.py
"""
import os
import sys

# allow importing from ./frontend if needed
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")
if FRONTEND_DIR not in sys.path:
    sys.path.insert(0, FRONTEND_DIR)

from frontend.app import main  # type: ignore


if __name__ == "__main__":
    main()


