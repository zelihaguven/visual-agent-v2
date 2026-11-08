"""HTTP API giriş noktası."""

from typing import Literal

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel

from visual_agent.settings import Settings


class HealthResponse(BaseModel):
    status: Literal["ok"]
    auth_enabled: bool


def _health_router(settings: Settings) -> APIRouter:
    router = APIRouter(prefix="/api")

    @router.get("/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        return HealthResponse(status="ok", auth_enabled=settings.auth_enabled)

    return router


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved = settings if settings is not None else Settings()
    app = FastAPI(title="Visual Agent")
    app.include_router(_health_router(resolved))
    return app
