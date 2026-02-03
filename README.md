# CyberSentinel — Threat Intelligence Platform


CyberSentinel is a real-time cybersecurity threat intelligence platform built for rapid incident analysis, visualization, and operational monitoring. It combines a FastAPI backend with a Streamlit dashboard to provide a single pane of glass for security teams. The project is designed to be easy to run locally, straightforward to containerize, and simple to extend.

## Project Overview
CyberSentinel ingests incident data (CSV fallback or MongoDB), normalizes it into a consistent schema, and surfaces insights through a live dashboard. The backend exposes a clean REST API, while the frontend visualizes incidents, severity trends, and geographic distribution.

## Features
- **Real-time dashboard** with interactive incident exploration
- **Standardized incident API** for reliable integrations
- **Geographic visualization** of incidents across India
- **Health checks** for service readiness monitoring
- **CSV fallback** when MongoDB is unavailable
- **Developer-friendly setup** with one-click VS Code task
- **CI-ready workflow** for automated tests and linting


## Folder Structure
```
CyberSentinel/
## Contribution Guide
1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/my-change`.
3. Run tests: `python -m pytest -q backend/tests`.
4. Commit with a clear message.
5. Open a pull request with context and screenshots where applicable.

## License
This project is open source. Review the repository license for terms and conditions.
