"""Uygulamanın tek ayar nesnesi: başlangıçta doğrulanır, sonra değişmez."""

from typing import Literal

from pydantic import AliasChoices, AnyHttpUrl, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="VA_",
        env_file=".env",
        extra="ignore",
        frozen=True,
    )

    qdrant_url: AnyHttpUrl = AnyHttpUrl("http://localhost:6333")
    qdrant_path: str | None = None
    database_path: str = "data/visual_agent.db"
    worker_poll_seconds: float = Field(default=5.0, gt=0)
    worker_in_process: bool = True
    # Açıkken modeller yalnız yerel önbellekten yüklenir; internetsiz açılış (ilk kurulumdan sonra).
    # Yalnız yerel başlatıcı (apps.local) okur; Docker'da HF_HUB_OFFLINE ortamda verilir.
    models_offline: bool = False
    # Yerel arayüzün portu; Docker'daki nginx eşlemesiyle aynı ad (önek yok).
    web_port: int = Field(
        default=8080, gt=0, le=65535, validation_alias=AliasChoices("WEB_PORT", "web_port")
    )
    storage_directory: str = "data/documents"
    web_directory: str | None = "apps/web/dist"
    soffice_path: str | None = None
    tesseract_path: str | None = None
    openrouter_api_key: SecretStr | None = None
    openrouter_url: AnyHttpUrl = AnyHttpUrl("https://openrouter.ai/api/v1")
    answer_model: str = "google/gemma-4-26b-a4b-it"
    answer_providers: tuple[str, ...] = ("deepinfra", "venice", "parasail")
    answer_max_tokens: int = Field(default=1200, gt=0)
    answer_first_token_seconds: float = Field(default=2.5, gt=0)
    stream_runaway_limit: int = Field(default=40, gt=0)
    helper_model: str = "google/gemma-4-26b-a4b-it"
    helper_providers: tuple[str, ...] = ("nextbit", "venice")
    stt_model: str = "elevenlabs/scribe-v2"
    stt_language: str = "tr"
    tts_model: str = "google/gemini-3.8-flash-lite-tts"
    tts_voice: str = "Kore"
    tts_format: Literal["mp3", "pcm"] = "pcm"

    @field_validator(
        "qdrant_path", "web_directory", "soffice_path", "tesseract_path", mode="before"
    )
    @classmethod
    def empty_path_means_server(cls, value: object) -> object:
        """Boş yol verilmemiş sayılır: Qdrant sunucusu, arayüzsüz API, araçlar PATH'ten."""
        return None if isinstance(value, str) and not value.strip() else value
