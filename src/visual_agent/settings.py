"""Uygulamanın tek ayar nesnesi: başlangıçta doğrulanır, sonra değişmez."""

from typing import Literal, Self

from pydantic import AnyHttpUrl, Field, PostgresDsn, SecretStr, model_validator
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
    storage_directory: str = "data/documents"
    openrouter_api_key: SecretStr | None = None
    openrouter_url: AnyHttpUrl = AnyHttpUrl("https://openrouter.ai/api/v1")
    answer_model: str = "google/gemma-4-26b-a4b-it"
    answer_providers: tuple[str, ...] = ("deepinfra", "venice", "parasail")
    answer_max_tokens: int = Field(default=1200, gt=0)
    answer_first_token_seconds: float = Field(default=2.5, gt=0)
    stream_runaway_limit: int = Field(default=40, gt=0)
    translation_model: str = "google/gemma-4-26b-a4b-it"
    translation_providers: tuple[str, ...] = ("nextbit", "venice")
    stt_model: str = "elevenlabs/scribe-v2"
    stt_language: str = "tr"
    tts_model: str = "google/gemini-3.8-flash-lite-tts"
    tts_voice: str = "Kore"
    tts_format: Literal["mp3", "pcm"] = "pcm"

    @model_validator(mode="after")
    def reject_unimplemented_login(self) -> Self:
        if self.auth_enabled:
            raise ValueError("giriş henüz uygulanmadı; VA_AUTH_ENABLED=false bırakın")
        return self
