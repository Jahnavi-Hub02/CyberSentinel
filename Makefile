PYTHON ?= python

.PHONY: run backend frontend test lint

run:
	$(PYTHON) scripts/run_services.py

backend:
	$(PYTHON) -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload

frontend:
	streamlit run frontend/app.py --server.port 8501

test:
	pytest

