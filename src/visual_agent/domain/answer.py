"""Modelin cevabı, modele verilen kaynaklar ve doğrulama sonucu."""

from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

MIN_CLARIFY_OPTIONS = 1


class AnswerKind(StrEnum):
    ANSWER = "cevap"
    CLARIFY = "netlestirme"
    NOT_FOUND = "bulunamadi"


class VerificationStatus(StrEnum):
    VERIFIED = "verified"
    PARTIAL = "partial"
    FAILED = "failed"
    NOT_FOUND = "not_found"
    CLARIFY = "clarify"


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)


class Quote(_Frozen):
    source_no: int = Field(alias="kaynak_no")
    text: str = Field(alias="metin")


class ModelItem(_Frozen):
    text: str = Field(alias="metin")
    quotes: tuple[Quote, ...] = Field(default=(), alias="alintilar")
    code_source_no: int | None = Field(default=None, alias="kod_kaynak_no")

    @model_validator(mode="after")
    def require_evidence(self) -> Self:
        if not self.quotes and self.code_source_no is None:
            raise ValueError("öğenin alıntısı ya da kod kaynağı olmalı")
        return self


class ClarifyOption(_Frozen):
    source_no: int = Field(alias="kaynak_no")


class ClarifyRequest(_Frozen):
    question: str = Field(alias="soru")
    options: tuple[ClarifyOption, ...] = Field(alias="secenekler")


class ModelAnswer(_Frozen):
    kind: AnswerKind = Field(alias="tur")
    items: tuple[ModelItem, ...] = Field(default=(), alias="cevap")
    clarify: ClarifyRequest | None = Field(default=None, alias="netlestirme")
    has_conflict: bool = Field(default=False, alias="celiski_var")

    @model_validator(mode="after")
    def require_consistent_kind(self) -> Self:
        if self.kind is AnswerKind.NOT_FOUND and self.items:
            raise ValueError("bulunamadı cevabı boş olmalı")
        if self.kind is AnswerKind.CLARIFY:
            enough = self.clarify is not None and len(self.clarify.options) >= MIN_CLARIFY_OPTIONS
            if not enough or self.items:
                raise ValueError("netleştirme en az iki seçenek ister ve cevap içeremez")
        return self


class PromptSource(_Frozen):
    number: int
    text: str
    context: str = ""
    ocr_uncertain: tuple[str, ...] = ()
    is_code: bool = False
    from_ocr: bool = False


class ItemCheck(_Frozen):
    ok: bool
    from_figure: bool
    problems: tuple[str, ...]
    source_numbers: tuple[int, ...]
    quote: str | None = None
    """Cümle yalnız kaynakta yazmayan birim yüzünden geçemediyse doğrulanmış alıntısı."""


class AnswerVerification(_Frozen):
    status: VerificationStatus
    items: tuple[ItemCheck, ...] = ()
    problems: tuple[str, ...] = ()
    clarify_options: tuple[int, ...] = ()
