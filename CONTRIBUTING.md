# Contributing to CyberSentinel

Thanks for your interest in improving **CyberSentinel: India’s Cyber Incident Monitoring Dashboard**.
This guide explains how to set up a dev environment, run tests, and open good pull requests.

---

## 1. Development Setup

From the project root:

```bash
git clone https://github.com/Jahnavi-Hub02/CyberSentinel.git
cd CyberSentinel-main/CyberSentinel-main
```

Create and activate a virtual environment:

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows (PowerShell)
# or
source .venv/bin/activate      # macOS / Linux
```

Install dependencies:

```bash
pip install -r backend/requirements.txt
```

Run the app:

```bash
python scripts/run_services.py
```

The dashboard will be available at `http://localhost:8501`.

---

## 2. Code Style

- Use **Python 3.10+** type hints where reasonable.
- Keep functions small and focused.
- Prefer explicit, descriptive names (`load_incident_csv`, `build_map_section`) over abbreviations.
- Follow the existing structure:
  - `backend/` for API, data, ML
  - `frontend/` for Streamlit UI
  - `scripts/` for helper runners

If you introduce a new module or pattern, add a short comment or docstring explaining it.

---

## 3. Running Tests

From the project root, with the virtualenv active:

```bash
pytest
```

This runs unit and integration tests under `backend/tests/`.

If you modify anything in `backend/`, please make sure tests pass (and ideally add new tests).

To run the optional integration smoke test (requires a running backend on `127.0.0.1:8000`):

```bash
RUN_INTEGRATION=1 pytest backend/tests/test_integration_smoke.py
```

---

## 4. Opening a Pull Request

When you open a PR:

- Describe **what** you changed and **why**.
- Mention any new configuration or environment variables.
- Note anything that might break existing usage.
- Include screenshots if you changed the UI.

Good PR title examples:

- `Add ML anomaly score badges to incident table`
- `Improve geocoder coverage for Tier‑2 Indian cities`
- `Refine README and add contributor guide`

---

## 5. Issues & Feature Requests

If you find a bug or have an idea:

- Check existing issues first.
- When filing a new issue, include:
  - Clear title
  - Steps to reproduce (if bug)
  - Expected vs actual behavior
  - Screenshots or logs if helpful

Thanks again for helping improve CyberSentinel!
