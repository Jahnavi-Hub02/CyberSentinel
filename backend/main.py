from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.websockets import WebSocket
import uvicorn

from backend.routers.incidents import router as incidents_router
from backend.db.mongo import init_mongo, close_mongo


def create_app() -> FastAPI:
    app = FastAPI(title="CyberSentinel API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(incidents_router, prefix="/api/incidents", tags=["incidents"])

    @app.get("/api/health")
    async def health() -> JSONResponse:
        return JSONResponse({"status": "ok"})

    @app.on_event("startup")
    async def on_startup() -> None:
        await init_mongo()

    @app.on_event("shutdown")
    async def on_shutdown() -> None:
        await close_mongo()

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


