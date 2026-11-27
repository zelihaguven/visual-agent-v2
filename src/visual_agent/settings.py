"""Uygulamanın tek ayar nesnesi: başlangıçta doğrulanır, sonra değişmez."""

from typing import Literal

from pydantic import AliasChoices, AnyHttpUrl, Field, SecretStr, field_validator, model_validator
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
    # Açıkken modeller yalnız yerel önbellekten yüklenir; internetsiz açılış (ilk kurulumdan sonra).
    # Yalnız yerel başlatıcı (apps.local) okur.
    models_offline: bool = False
    # Yerel arayüzün portu; .env'de önek olmadan yazılır (WEB_PORT).
    web_port: int = Field(
        default=8080, gt=0, le=65535, validation_alias=AliasChoices("WEB_PORT", "web_port")
    )
    storage_directory: str = "data/documents"
    web_directory: str | None = "apps/web/dist"
    soffice_path: str | None = None
    tesseract_path: str | None = None
    # Metin katmanı olmayan sayfaların okuyucusu (PaddleOCR-VL): "local" ya da
    # "<arka uç>@<adres>", ör. "mlx-vlm-server@http://localhost:8111/". Boşsa bu sayfaları
    # olan belgeler okuyucuyu bekler.
    page_reader: str | None = None
    # Sayfa okuyucusunun ikinci okuması ve şekil blokları (karar 0035; OpenRouter, yalnız ZDR).
    # Anahtar yoksa ikinci okuma Tesseract, şekil blokları okunmaz. Bulut cevapları önbellekte
    # saklanır: aynı kırpıntı yeniden işlemede ikinci kez ödenmez.
    reader_model: str = "qwen/qwen3-vl-30b-a3b-instruct"
    reader_figure_check_model: str = "google/gemma-4-26b-a4b-it"
    reader_cache_directory: str = "data/okuma-onbellegi"
    openrouter_api_key: SecretStr | None = None
    openrouter_url: AnyHttpUrl = AnyHttpUrl("https://openrouter.ai/api/v1")
    answer_model: str = "google/gemma-4-26b-a4b-it"
    answer_providers: tuple[str, ...] = ("makora", "deepinfra")
    answer_max_tokens: int = Field(default=1200, gt=0)
    answer_first_token_seconds: float = Field(default=2.5, gt=0)
    stream_runaway_limit: int = Field(default=40, gt=0)
    helper_model: str = "google/gemma-4-26b-a4b-it"
    helper_providers: tuple[str, ...] = ("parasail", "venice", "nextbit")
    stt_model: str = "elevenlabs/scribe-v2"
    stt_language: str = "tr"
    tts_model: str = "google/gemini-3.8-flash-lite-tts"
    tts_voice: str = "Kore"
    tts_format: Literal["mp3", "pcm"] = "pcm"

    @field_validator(
        "qdrant_path",
        "web_directory",
        "soffice_path",
        "tesseract_path",
        "page_reader",
        mode="before",
    )
    @classmethod
    def empty_path_means_server(cls, value: object) -> object:
        """Boş yol verilmemiş sayılır: Qdrant sunucusu, arayüzsüz API, araçlar PATH'ten."""
        return None if isinstance(value, str) and not value.strip() else value

    @field_validator("page_reader")
    @classmethod
    def reader_setting_is_valid(cls, value: str | None) -> str | None:
        """Geçersiz okuyucu ayarı açılışta durdurur; işçinin içinde sessizce düşmez."""
        from visual_agent.ingest.page_reader import parse_reader_setting

        parse_reader_setting(value)
        return value

    @model_validator(mode="after")
    def figure_check_is_another_model(self) -> "Settings":
        """Şekil bloğunu okuyan model kendi okumasını denetleyemez: aynı hatayı iki kez yapar ve
        değer doğrulanmış görünür (karar 0035)."""
        if self.reader_figure_check_model.strip() == self.reader_model.strip():
            raise ValueError(
                "VA_READER_FIGURE_CHECK_MODEL, VA_READER_MODEL ile aynı olamaz: şekil bloğunu"
                " başka bir model denetlemeli."
            )
        return self
