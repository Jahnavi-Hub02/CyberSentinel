"""Canonical FastAPI app for CyberSentinel.
This contains the application factory so `uvicorn backend.app:app` is the single
backend entry point for development and production deployments.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.incidents import router as incidents_router
from .api.detection import router as detection_router
from .db.mongo import init_mongo, close_mongo


from contextlib import asynccontextmanager


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
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(incidents_router, prefix="/api/incidents", tags=["incidents"])
    app.include_router(detection_router, prefix="/api", tags=["ml"])

    # Health endpoint
    from .api.health import router as health_router
    app.include_router(health_router, prefix="/api", tags=["health"])

    # Insights (top locations, pre-aggregated for map performance)
    from .routers.insights import router as insights_router
    app.include_router(insights_router, prefix="/api", tags=["insights"])


    return app


# Expose the app for uvicorn
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, reload=True)
