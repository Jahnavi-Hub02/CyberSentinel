"""Canonical FastAPI app for CyberSentinel.

Run the backend with:
    uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload
"""
from __future__ import annotations
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers.incidents import router as incidents_router
from .routers.detection import router as detection_router
from .routers.health import router as health_router
from .routers.insights import router as insights_router
from .db.mongo import init_mongo, close_mongo

from contextlib import asynccontextmanager


def _cors_origins() -> list[str]:
    """Return the allowed CORS origins for local frontend access."""
    env_value = os.getenv("CORS_ORIGINS")
    if env_value:
        return [origin.strip() for origin in env_value.split(",") if origin.strip()]
    return [
        "http://localhost:8501",
        "http://127.0.0.1:8501",
    ]


def create_app() -> FastAPI:
    # Use lifespan handler for startup/shutdown (replaces deprecated on_event)
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await init_mongo()
        try:
            yield
        finally:
            await close_mongo()

    app = FastAPI(title="CyberSentinel API", version="1.0.0", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins(),
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(incidents_router, prefix="/api/incidents", tags=["incidents"])
    app.include_router(detection_router, prefix="/api", tags=["ml"])

    # Health endpoint (both /health and /api/health)
    app.include_router(health_router, tags=["health"])
    app.include_router(health_router, prefix="/api", tags=["health"])

    # Insights (top locations, pre-aggregated for map performance)
    app.include_router(insights_router, prefix="/api", tags=["insights"])

    return app


# Expose the app for uvicorn
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, reload=True)
