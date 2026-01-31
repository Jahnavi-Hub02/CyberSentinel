# ML Detection Guide (Archived Demo)

This document explains how to use CyberSentinel's ML detection system for development and testing. Demo scripts are archived under `experiments/` and are intentionally not part of the active codebase.

## Quick Demo (recommended via API)

1. Start the backend:

```bash
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

2. Check ML status:

```bash
curl http://127.0.0.1:8000/api/ml/status
```

3. Train a model (POST JSON payload):

```bash
curl -X POST http://127.0.0.1:8000/api/ml/train -H "Content-Type: application/json" -d '{"incidents": [...], "contamination": 0.05}'
```

4. Run detection on a batch:

```bash
curl -X POST http://127.0.0.1:8000/api/ml/detect -H "Content-Type: application/json" -d '{"incidents": [...], "auto_severity": true}'
```

## Notes

- Demo scripts are archived and will not be executed as part of normal runs. See `experiments/` for archived examples.
- ML functionality will store results in MongoDB if configured; otherwise it operates in-memory or saves to JSON fallback.
- For CI and offline usage, training/detection can be performed on local CSV exports of the `data/` folder.
