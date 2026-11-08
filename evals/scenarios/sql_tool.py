"""Kurgusal SQL aracı: kılavuz, kolon sözlüğü ve kayıtlı sorgular."""

from functools import partial
from random import Random

from evals.content import (
    CodeBlock,
    DocumentContent,
    Scenario,
    ScenarioDocument,
    TableBlock,
    TextBlock,
    source_for,
)
from evals.gold import Carrier, GoldDocument, GoldQuestion, Mess, Outcome, QuestionKind

DOMAIN = "sql"
TOOL = "Kuzey Sorgu"
SHARED_COLUMN = "MUSTERI_KODU"
TABLE_NAMES = ("SIPARIS_BASLIK", "SIPARIS_KALEM", "STOK_HAREKET", "FATURA_BASLIK", "DEPO_SAYIM")
COLUMN_NAMES = ("TESLIM_TARIHI", "DEPO_KODU", "BIRIM_FIYAT", "KALEM_ADEDI")
ABSENT_TERM = "yedekleme"

make_question = partial(GoldQuestion, domain=DOMAIN)


def _document(
    doc_id: str,
    suffix: str,
    carrier: Carrier,
    title: str,
    blocks: tuple[TextBlock | TableBlock | CodeBlock, ...],
    *mess: Mess,
) -> ScenarioDocument:
    return ScenarioDocument(
        gold=GoldDocument(
            doc_id=doc_id,
            filename=f"{doc_id}.{suffix}",
            domain=DOMAIN,
            carrier=carrier,
            mess=mess,
        ),
        content=DocumentContent(title=title, blocks=blocks),
    )


def _catalog(table: str, shared_length: int, column: str, length: int) -> TableBlock:
    return TableBlock(
        title="Kolon sözlüğü",
        headers=("Tablo", "Kolon", "Tip", "Uzunluk"),
        rows=(
            (table, SHARED_COLUMN, "VARCHAR", str(shared_length)),
            (table, column, "VARCHAR", str(length)),
        ),
    )


def _command_fields(
    document: ScenarioDocument, block_index: int, command: str, values: tuple[str, ...]
) -> dict[str, object]:
    return {
        "outcome": Outcome.ANSWERED,
        "expected_values": values,
        "evidence": command,
        "sources": (source_for(document, block_index),),
    }


def _not_found(question_id: str, text: str, **extra: object) -> GoldQuestion:
    return make_question(
        question_id=question_id,
        text=text,
        kind=QuestionKind.NOT_IN_DOCUMENT,
        outcome=Outcome.NOT_FOUND,
        absent_term=ABSENT_TERM,
        **extra,
    )


def build_sql_tool(rng: Random) -> Scenario:
    first, second, third, fourth, _ = rng.sample(TABLE_NAMES, 5)
    column_a, column_b, column_c, _ = rng.sample(COLUMN_NAMES, 4)
    lengths = rng.sample(range(12, 96), 6)
    timeout = rng.randint(60, 180)
    old, new = "SIP_TARIH", "SIPARIS_TARIHI"
    rename = f"ALTER TABLE {first} RENAME COLUMN {old} TO {new};"
    add = f"ALTER TABLE {first} ADD {column_a} VARCHAR({lengths[0]});"

    manual = _document(
        "sql-kilavuz",
        "pdf",
        Carrier.PDF,
        f"{TOOL} Kullanım Kılavuzu",
        (CodeBlock("Kolon adını değiştirme", rename), CodeBlock("Yeni kolon ekleme", add)),
    )
    screenshot = _document(
        "sql-ekran",
        "docx",
        Carrier.SCREENSHOT,
        f"{TOOL} Tablo Notları",
        (
            TextBlock("Açıklama", "Kolonlar aşağıdaki ekran görüntüsünde listelenmiştir."),
            _catalog(second, lengths[1], column_b, lengths[2]),
        ),
    )
    dictionary = _document(
        "sql-sozluk",
        "xlsx",
        Carrier.XLSX,
        "Veri Sözlüğü",
        (_catalog(third, lengths[3], column_c, lengths[4]),),
        Mess.MULTI_SHEET,
    )
    saved_query = _document(
        "sql-rapor",
        "sql",
        Carrier.SQL_TEXT,
        "Aylık ciro raporu",
        (CodeBlock("Aylık ciro raporu", f"SELECT SUM(TUTAR) FROM {fourth};"),),
    )
    notes = _document(
        "sql-notlar",
        "docx",
        Carrier.DOCX,
        f"{TOOL} Setup Notes",
        (
            TextBlock("Connection", f"Query timeout default value is {timeout} seconds."),
            TextBlock("Bağlantı", "Bağlantı ayarları yönetici tarafından değiştirilir."),
        ),
        Mess.MIXED_LANGUAGE,
    )

    conversation = {"conversation_id": "sql-sohbet-1"}
    screenshot_length = str(lengths[2])
    questions = [
        make_question(
            question_id="sql-kolon-adi",
            text=f"{TOOL}'da {first} tablosunda {old} kolonunun adını {new} yapan komut nedir?",
            kind=QuestionKind.DIRECT,
            **_command_fields(manual, 0, rename, (first, old, new)),
        ),
        make_question(
            question_id="sql-ekran-uzunluk",
            text=f"{second} tablosunda {column_b} kolonunun uzunluğu kaç?",
            kind=QuestionKind.IN_IMAGE,
            **_command_fields(
                screenshot,
                1,
                f"{second} {column_b} VARCHAR {screenshot_length}",
                (screenshot_length,),
            ),
        ),
        make_question(
            question_id="sql-sozluk-uzunluk",
            text=f"{third} tablosunda {column_c} uzunluğu kaç?",
            kind=QuestionKind.TABLE_LOOKUP,
            outcome=Outcome.ANSWERED,
            expected_values=(str(lengths[4]),),
            evidence=f"{third} {column_c} VARCHAR {lengths[4]}",
            sources=(source_for(dictionary, 0, 1),),
        ),
        make_question(
            question_id="sql-rapor-tablo",
            text="Aylık ciro raporu hangi tabloyu okuyor?",
            kind=QuestionKind.DIRECT,
            **_command_fields(saved_query, 0, f"SUM(TUTAR) {fourth}", (fourth,)),
        ),
        make_question(
            question_id="sql-zaman-asimi",
            text="Sorgu zaman aşımı varsayılan olarak kaç saniye?",
            kind=QuestionKind.DIRECT,
            **_command_fields(notes, 0, f"timeout {timeout}", (str(timeout),)),
        ),
        make_question(
            question_id="sql-netlestir",
            text=f"{SHARED_COLUMN} kolonunun uzunluğu kaç?",
            kind=QuestionKind.CLARIFY,
            outcome=Outcome.CLARIFY,
            differing_values=(str(lengths[1]), str(lengths[3])),
        ),
        _not_found("sql-yok", f"{TOOL}'da yedekleme nasıl yapılır?"),
        make_question(
            question_id="sql-sohbet-1-t1",
            text=f"{first} tablosunda {old} kolonunu {new} olarak nasıl değiştiririm?",
            kind=QuestionKind.DIRECT,
            turn=1,
            **conversation,
            **_command_fields(manual, 0, rename, (first, old, new)),
        ),
        make_question(
            question_id="sql-sohbet-1-t2",
            text="Peki yeni kolon eklerken komut ne?",
            kind=QuestionKind.FOLLOW_UP,
            turn=2,
            **conversation,
            **_command_fields(manual, 1, add, (first, column_a)),
        ),
        _not_found("sql-sohbet-1-t3", "Peki yedekleme nasıl yapılır?", turn=3, **conversation),
    ]
    return Scenario(
        documents=(manual, screenshot, dictionary, saved_query, notes),
        questions=tuple(questions),
    )
