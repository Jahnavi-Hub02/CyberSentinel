# This module was removed in favor of `backend.app` as the single canonical backend entry point.
# If you are looking for application startup logic, use `backend.app.create_app()` or
# run the server with `uvicorn backend.app:app`.
print('backend/main.py has been retired; use backend.app instead')
import sys
sys.exit(0)

