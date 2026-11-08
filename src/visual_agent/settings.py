"""Uygulamanın tek ayar nesnesi: başlangıçta doğrulanır, sonra değişmez."""

from typing import Self

from pydantic import AnyHttpUrl, Field, PostgresDsn, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="VA_",
        env_file=".env",
        extra="ignore",
        frozen=True,
    )

    auth_enabled: bool = False
    qdrant_url: AnyHttpUrl = AnyHttpUrl("http://localhost:6333")
    database_url: PostgresDsn | None = None
    worker_poll_seconds: float = Field(default=5.0, gt=0)

    @model_validator(mode="after")
    def reject_unimplemented_login(self) -> Self:
        if self.auth_enabled:
            raise ValueError("giriş henüz uygulanmadı; VA_AUTH_ENABLED=false bırakın")
        return self
