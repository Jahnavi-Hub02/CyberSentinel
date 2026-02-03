from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/health")
async def health() -> JSONResponse:
    """Lightweight health check for load balancers and local scripts."""
    return JSONResponse({"status": "online"})
