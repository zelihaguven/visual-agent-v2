"""Soru hattının adımları. Her adım yeni bir durum döndürür."""

import asyncio
import logging
import re
import time
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, replace

from visual_agent.ask.agreement import agreed_answer, candidate_documents
from visual_agent.ask.deps import AskDeps, AskRequest
from visual_agent.ask.language import detect_language
from visual_agent.ask.streaming import INCOMPLETE_MESSAGE, StreamAssembler
from visual_agent.conversation.grounding import marked_tokens
from visual_agent.domain.answer import (
    AnswerKind,
    ItemCheck,
    ModelAnswer,
    ModelItem,
    VerificationStatus,
)
from visual_agent.domain.document import Chunk, ChunkKind
from visual_agent.domain.result import (
    Answered,
    AnsweredItem,
    AskResult,
    Citation,
    Clarify,
    ClarifyChoice,
    Failed,
    Hit,
    NotFound,
)
from visual_agent.generation.openrouter import AttemptRecord, ServiceUnavailable, StreamCallbacks
from visual_agent.generation.parse import ParseFailure, parse_answer
from visual_agent.generation.sources import build_user_message, to_prompt_sources
from visual_agent.verification.answer import (
    ABSENCE_CLAIM,
    Sources,
    code_source_number,
    safe_clarify_question,
    verify_answer,
)
from visual_agent.verification.text import identifiers_in, normalize

logger = logging.getLogger(__name__)

_MAX_EXACT_CHUNKS_PER_IDENTIFIER = 2
_MIN_CLARIFY_DOCUMENTS = 2
_MAX_CLARIFY_DOCUMENTS = 4
"""Netleştirmede en çok bu kadar belge düğmesi; sorudaki kod da en çok bu kadar belgeye daraltır
(kapsam netleştirilebilir kalır)."""
_SERVICE_DOWN = "Cevap servisi şu an kullanılamıyor. Bulunan kaynak sayfaları aşağıda."
_MODEL_FAILED = "Model güvenilir bir cevap üretemedi. Değeri kaynaktan kontrol edin."


Translation = tuple[str, bool, bool]
"""BM25 sorgusu, çevirinin denenip denenmediği ve düşüp düşmediği."""


@dataclass(frozen=True)
class AskState:
    request: AskRequest
    language: str = "tr"
    allowed: tuple[str, ...] = ()
    scope: tuple[str, ...] | None = None
    exact_chunks: tuple[Chunk, ...] = ()
    hits: tuple[Hit, ...] = ()
    answer: ModelAnswer | None = None
    cost_usd: float = 0.0
    provider: str | None = None
    first_verified_seconds: float | None = None
    result: AskResult | None = None
    resolved_question: str | None = None
    inherited_doc_ids: tuple[str, ...] = ()
    scope_inherited: bool = False
    scope_narrowed: bool = False
    context_resolved: bool = True
    translation: "asyncio.Task[Translation] | None" = None
    """Niyet adımında erken başlatılan sorgu çevirisi; arama adımı sonucunu bekler."""
    translate_seconds: float | None = None
    """Aramanın çeviriyi beklediği süre (çeviri erken başladıysa çağrının tamamı değil)."""
    translation_failed: bool = False
    bm25_query: str | None = None
    """BM25'e giden sorgu (çeviri yapıldıysa çevrilmiş hali); teşhis için kayda girer."""
    model_question: str | None = None
    """Cevap modeline giden soru metni (çeviri değil, özgün ya da tamamlanmış soru)."""
    raw_output: str | None = None
    """Cevap modelinin ham çıktısı, alıntılar dahil; teşhis için kayda girer."""
    provider_attempts: int = 0
    provider_seconds: float = 0.0
    provider_errors: tuple[tuple[str, str], ...] = ()

    @property
    def question(self) -> str:
        return self.resolved_question or self.request.question


def _citation(hit: Hit) -> Citation:
    chunk = hit.chunk
    return Citation(
        chunk_id=chunk.chunk_id, doc_id=chunk.doc_id, title=chunk.title, location=chunk.location
    )


def _search_domain(state: AskState) -> tuple[str, ...]:
    return state.scope if state.scope is not None else state.allowed


def _exact_chunks(identifiers: Sequence[str], state: AskState, deps: AskDeps) -> tuple[Chunk, ...]:
    """Kodu kendi metninde taşıyan parçalar kaynakların başına eklenir.

    Başlıkta ya da bölüm adında geçen kod ("PNT-1162 ölçü tablosu"), metninde kod geçmeyen
    satırları öne geçirmez; kodun hangi belgede olduğu kararı ise başlık dahil verilir. Aranan
    belgelerden birinin adı olan kod yalnız kapsamı belirler.
    """
    domain = _search_domain(state)
    chunks: dict[str, Chunk] = {}
    for identifier in identifiers:
        if deps.catalog.is_document_name(identifier, domain):
            continue
        found = deps.identifiers.chunks_naming(identifier, domain)
        ordered = sorted(found, key=lambda chunk: chunk.kind is not ChunkKind.TABLE_ROW)
        for chunk in ordered[:_MAX_EXACT_CHUNKS_PER_IDENTIFIER]:
            chunks.setdefault(chunk.chunk_id, chunk)
    return tuple(chunks.values())


def _code_not_found(missing: Sequence[str], state: AskState, deps: AskDeps) -> NotFound:
    suggested = tuple(
        dict.fromkeys(
            doc_id
            for identifier in missing
            for doc_id in deps.identifiers.documents_with(identifier)
            if doc_id in state.allowed
        )
    )
    codes = ", ".join(item.upper() for item in missing)
    choices = tuple(
        ClarifyChoice(doc_id=doc_id, label=deps.catalog.title(doc_id))
        for doc_id in suggested[:_MAX_CLARIFY_DOCUMENTS]
    )
    if suggested and state.scope_inherited:
        # Kod başka belgede var; arayüz "bu belgede yok" der ve "Tüm belgelerde ara" önerir.
        return NotFound(reason="", suggestions=choices)
    # Kod kapsam dışındaki bir belgede varsa (seçilen, adı geçen ya da önceki turun belgesi)
    # "belgelerde geçmiyor" denmez; o belge düğme olarak önerilir.
    place = "seçilen belgelerde" if suggested else "belgelerde"
    return NotFound(reason=f"{codes} {place} geçmiyor.", suggestions=choices)


CONTEXT_GONE_QUESTION = (
    "Önceki belge silinmiş ya da şu an yeniden işleniyor. Hangi belgeden soruyorsunuz?"
)


def _context_documents_gone(
    state: AskState, deps: AskDeps, allowed: Sequence[str], explicit: Sequence[str]
) -> bool:
    """Takip sorusunun belgelerinin hepsi gitti ve kullanıcı yeni belge ya da kod söylemedi.

    Tamamlanan soru kodu bağlamdan taşıdığı için yalnız kullanıcının kendi mesajına bakılır.
    """
    if not state.inherited_doc_ids or explicit:
        return False
    if any(doc in allowed for doc in state.inherited_doc_ids):
        return False
    own = state.request.question
    if deps.catalog.mentioned_in(own, allowed):
        return False
    return not (identifiers_in(own) or deps.identifiers.codes_in_speech(own))


async def resolve_scope(state: AskState, deps: AskDeps) -> AskState:
    """Kapsamı belirler; kod hiçbir yerde yoksa arama ve model çalışmadan durur."""
    request = state.request
    allowed = deps.catalog.doc_ids()
    mentioned = deps.catalog.mentioned_in(state.question, allowed)
    explicit = tuple(doc for doc in request.doc_ids or () if doc in allowed)
    inherited = tuple(doc for doc in state.inherited_doc_ids if doc in allowed)
    scope = explicit or mentioned or inherited or None
    if _context_documents_gone(state, deps, allowed, explicit):
        return replace(
            state,
            allowed=allowed,
            scope=state.inherited_doc_ids,
            result=Clarify(question=CONTEXT_GONE_QUESTION),
        )
    current = replace(
        state,
        language=detect_language(state.question),
        allowed=allowed,
        scope=scope,
        scope_inherited=bool(inherited) and not explicit and not mentioned,
    )
    identifiers = sorted(
        identifiers_in(state.question) | deps.identifiers.codes_in_speech(state.question)
    )
    domain = _search_domain(current)
    missing = [item for item in identifiers if not deps.identifiers.lookup(item, domain)]
    if missing and len(missing) == len(identifiers):
        return replace(current, result=_code_not_found(missing, current, deps))
    if scope is None and not request.all_documents:
        narrowed = _code_documents(identifiers, allowed, deps)
        current = replace(current, scope=narrowed, scope_narrowed=narrowed is not None)
    return replace(current, exact_chunks=_exact_chunks(identifiers, current, deps))


def _code_documents(
    identifiers: Sequence[str], allowed: Sequence[str], deps: AskDeps
) -> tuple[str, ...] | None:
    """Sorudaki kodların geçtiği belgeler: arama bunlara daralır.

    Netleştirme düğmesi sınırından çok belgede geçen kod (ortak bileşen kodu, ör. bütün tech
    pack'lerdeki iplik) daraltmaz; daraltan kodların belgeleri birleşir, birleşim de sınırı
    aşarsa ya da hiçbir kod daraltmıyorsa kapsam bütün belgeler kalır (None).
    """
    found: set[str] = set()
    for identifier in identifiers:
        having = {doc for doc in deps.identifiers.documents_with(identifier) if doc in allowed}
        if len(having) <= _MAX_CLARIFY_DOCUMENTS:
            found |= having
    documents = tuple(doc for doc in allowed if doc in found)  # katalog sırası
    return documents if 0 < len(documents) <= _MAX_CLARIFY_DOCUMENTS else None


async def _bm25_query(state: AskState, deps: AskDeps) -> Translation:
    """Çeviri yalnız soru dili ile belge dilleri farklıysa yapılır; denenip denenmediği ve
    düşüp düşmediği ayrıca döner. Düşen çeviride arama özgün soruyla yapılır: başka dildeki
    belgede zayıflar."""
    question = state.question
    targets = deps.catalog.languages(_search_domain(state))
    if deps.translator is None or all(target == state.language for target in targets):
        return question, False, False
    try:
        translated = await asyncio.wait_for(
            deps.translator(question, state.language, targets), deps.translation_limit_seconds
        )
    except Exception:
        logger.warning("Sorgu çevirisi kullanılamadı; özgün soruyla aranıyor", exc_info=True)
        return question, True, True
    return translated, True, False


def start_translation(state: AskState, deps: AskDeps) -> "asyncio.Task[Translation]":
    """Çeviriyi beklemeden başlatır: niyet sınıflandırıcısı da yardımcı modele ayrı bir çağrıdır
    ve ikisi art arda beklenince cevap yaklaşık 0,8 sn gecikiyordu (soru günlüğü, 2026-11-22)."""
    return asyncio.create_task(_bm25_query(state, deps))


def _with_exact_chunks(state: AskState, found: Sequence[Hit], top_k: int) -> tuple[Hit, ...]:
    exact = [Hit(chunk=chunk, score=1.0) for chunk in state.exact_chunks]
    known = {hit.chunk.chunk_id for hit in exact}
    return tuple([*exact, *(hit for hit in found if hit.chunk.chunk_id not in known)][:top_k])


_RELATIVE_RE = re.compile(
    r"\b(increments?|incremental|delta|deltas|differences?|fark(?:lar|ı|i)?|artış(?:lar|ı)?)\b",
    re.IGNORECASE,
)
"""Tablo notu değerlerin bir başka değere göre fark olduğunu söylüyor ("Grade Rule Display:
Increment"). Bu satırların sayısı ölçü değil, bedenler arası farktır. Yalnız tablo notuna bakılır:
"Incremental Updates" gibi bir başlığın altındaki metin fark değildir."""


_FILTER_CANDIDATES = 20
"""Fark filtresi kaynaklar 8'e kesilmeden önce bu kadar adaya uygulanır: ayıklanan satırın
yerine sıradaki parça girer (karar 0029). Hibrit aramanın birleştirdiği parça sayısıyla aynı
(`hybrid._FUSED_K`); filtre bir şey ayıklamazsa ilk 8 eskisiyle birebir aynıdır."""

ChunkOf = Callable[[str], Chunk | None]


def _same_table(row: Chunk, other: Chunk | None) -> bool:
    """Sayfadaki tablo satırları tablonun kutusunu taşır: aynı sayfa ve aynı ilk kutu aynı
    tablodur."""
    return (
        other is not None
        and other.kind is ChunkKind.TABLE_ROW
        and other.location.page == row.location.page
        and other.location.boxes[:1] == row.location.boxes[:1]
    )


def _is_note_row(last: Chunk, previous: Chunk | None, row: Chunk) -> bool:
    """Fark ifadesi yalnız son satırdaysa o satır nottur. Önceki satırda da geçiyorsa ifade bir
    sütun adıdır ("Fark: 2" her satırda yazılı): tablo fark tablosu sayılmaz. Tek satırlı tabloda
    not satırı ayırt edilemez."""
    return (
        previous is not None
        and _same_table(row, previous)
        and bool(_RELATIVE_RE.search(last.text))
        and not _RELATIVE_RE.search(previous.text)
    )


def _table_note(row: Chunk, chunk_of: ChunkOf) -> str:
    """Satırın tablo notu. Boşsa ve satır sayfada bir tablodaysa not komşu parçadan okunur: sayfa
    okuyucusu notu tablonun son satırı ya da tablodan hemen sonra aynı sayfada ayrı bir metin
    olarak verebiliyor (karar 0029). Okuyucu notu satıra yazdığında bu arama devreden çıkar.

    Parça kimliği "belge:sıra"dır; sonraki parça sıra + 1'dir.
    """
    if row.table_note or row.kind is not ChunkKind.TABLE_ROW:
        return row.table_note
    doc_id, _, position = row.chunk_id.rpartition(":")
    if row.location.page is None or not row.location.boxes or not position.isdigit():
        return ""
    index, last = int(position), row
    while (following := chunk_of(f"{doc_id}:{index + 1}")) is not None and _same_table(
        row, following
    ):
        index, last = index + 1, following
    if _is_note_row(last, chunk_of(f"{doc_id}:{index - 1}"), row):
        return last.text
    after = chunk_of(f"{doc_id}:{index + 1}")
    if (
        after is not None
        and after.kind is ChunkKind.TEXT
        and after.location.page == row.location.page
    ):
        return after.text
    return ""


def _without_relative_tables(
    question: str, hits: Sequence[Hit], chunk_of: ChunkOf
) -> tuple[Hit, ...]:
    """Fark tablosunun satırları, soru farkı sormuyorsa kaynak olmaz: model farkı değer diye
    verebiliyor ve alıntı kaynakta birebir olduğu için doğrulama bunu yakalayamıyor (karar
    0006)."""
    if _RELATIVE_RE.search(question):
        return tuple(hits)
    return tuple(hit for hit in hits if not _RELATIVE_RE.search(_table_note(hit.chunk, chunk_of)))


async def retrieve(state: AskState, deps: AskDeps) -> AskState:
    """Arama daima kapsamla sınırlıdır: katalogda yalnız hazır belgeler vardır."""
    domain = _search_domain(state)
    if not domain:
        return replace(state, result=NotFound())
    started = time.perf_counter()
    bm25_query, tried, failed = await (state.translation or _bm25_query(state, deps))
    waited = time.perf_counter() - started if tried else None
    state = replace(
        state, translate_seconds=waited, translation_failed=failed, bm25_query=bm25_query
    )
    query = state.question
    if state.request.doc_ids and len(domain) == 1:
        # Belge düğmeyle seçildi: ürün adı ve sayfa üst bilgisi belge içinde ayırt edici değil.
        query = deps.identifiers.without_repeated_phrases(query, domain[0])
        bm25_query = deps.identifiers.without_repeated_phrases(bm25_query, domain[0])
        state = replace(state, bm25_query=bm25_query)
    candidates = max(deps.top_k, _FILTER_CANDIDATES)
    found = await deps.retriever.search(query, bm25_query, domain, candidates)
    hits = _without_relative_tables(
        state.question, _with_exact_chunks(state, found, candidates), deps.identifiers.chunk
    )[: deps.top_k]
    if not hits:
        return replace(state, result=NotFound())
    if state.request.on_event is not None:
        sources = [_citation(hit).model_dump(mode="json") for hit in hits]
        state.request.on_event({"type": "sources", "sources": sources})
    return replace(state, hits=hits)


def user_text(state: AskState) -> tuple[str, str]:
    """Kullanıcının kendi metni: bu turun sorusu ve önceki turdan yalnız kullanıcıdan geldiği
    denetlenmiş sözcükler (kod, sayı, beden; is_grounded). Modelin tamamladığı soru girmez."""
    context = state.request.context
    previous = sorted(marked_tokens(context.question)) if context is not None else []
    return state.request.question, " ".join(previous)


def _stream_callbacks(
    state: AskState, sources: Sources
) -> tuple[StreamAssembler | None, StreamCallbacks | None]:
    if state.request.on_event is None:
        return None, None
    assembler = StreamAssembler(sources, state.language, state.request.on_event, *user_text(state))
    return assembler, StreamCallbacks(
        on_delta=assembler.feed, may_retry=assembler.may_retry, on_reset=assembler.reset
    )


def _partial_result(assembler: StreamAssembler, hits: Sequence[Hit], sources: Sources) -> Answered:
    return Answered(
        status=VerificationStatus.PARTIAL,
        items=tuple(
            _answered_item(item, check, hits, sources) for item, check in assembler.verified
        ),
        problems=(INCOMPLETE_MESSAGE,),
    )


def _with_attempts(state: AskState, attempts: Sequence[AttemptRecord]) -> AskState:
    """Sağlayıcı yedeğine düşüldü mü, hangi sağlayıcı neden düştü, toplam ne kadar bekletti."""
    return replace(
        state,
        provider_attempts=len(attempts),
        provider_seconds=sum(attempt.seconds for attempt in attempts),
        provider_errors=tuple((attempt.provider, attempt.error) for attempt in attempts),
    )


async def generate(state: AskState, deps: AskDeps) -> AskState:
    state = replace(state, model_question=state.question)
    citations = tuple(_citation(hit) for hit in state.hits)
    messages = [
        {"role": "system", "content": deps.system_prompt},
        {
            "role": "user",
            "content": build_user_message(state.hits, state.question, state.language),
        },
    ]
    sources = to_prompt_sources(state.hits, deps.catalog.language)
    assembler, callbacks = _stream_callbacks(state, sources)
    try:
        stream = await deps.answer_client.stream(messages, callbacks)
    except ServiceUnavailable as error:
        logger.exception("Cevap servisine ulaşılamadı")
        return replace(
            _with_attempts(state, error.attempts),
            result=Failed(reason=_SERVICE_DOWN, citations=citations),
        )
    current = replace(
        _with_attempts(state, stream.attempts),
        cost_usd=stream.cost_usd,
        provider=stream.provider,
        first_verified_seconds=assembler.first_verified_seconds if assembler else None,
        raw_output=stream.content,
    )
    if stream.incomplete and assembler is not None:
        assembler.interrupted()
        return replace(current, result=_partial_result(assembler, state.hits, sources))
    parsed = parse_answer(stream.content, stream.finish)
    if isinstance(parsed, ParseFailure):
        logger.warning("Model çıktısı okunamadı: %s %s", parsed.reason, parsed.detail)
        return replace(current, result=Failed(reason=_MODEL_FAILED, citations=citations))
    return replace(current, answer=parsed)


def _hit_at(number: int, hits: Sequence[Hit]) -> Hit | None:
    return hits[number - 1] if 1 <= number <= len(hits) else None


def _answered_item(
    item: ModelItem, check: ItemCheck, hits: Sequence[Hit], sources: Sources
) -> AnsweredItem:
    numbers = [n for n in check.source_numbers if 1 <= n <= len(hits)]
    number = code_source_number(item, sources)
    code_hit = _hit_at(number, hits) if number is not None else None
    return AnsweredItem(
        text=item.text,
        citations=tuple(_citation(hits[number - 1]) for number in dict.fromkeys(numbers)),
        verified=check.ok,
        from_ocr=check.from_ocr,
        code=code_hit.chunk.text if check.ok and code_hit is not None else None,
        problems=check.problems,
        source_quote=check.quote,
    )


def _relevant_documents(documents: Sequence[str], state: AskState, deps: AskDeps) -> list[str]:
    """Soruda bir kod ya da belge adı geçiyorsa yalnız onu taşıyan aday belgeler seçenek olur:
    model, soruda adı geçmeyen bir ürünün kaynağını da seçenek gösterebiliyor. Soru hiçbir
    adayı adlandırmıyorsa adayların hepsi kalır."""
    codes = identifiers_in(state.question) | deps.identifiers.codes_in_speech(state.question)
    named = set(deps.catalog.mentioned_in(state.question, documents))
    named.update(doc for doc in documents for code in codes if deps.identifiers.lookup(code, [doc]))
    return [doc for doc in documents if doc in named] or list(documents)


def _clarification(
    answer: ModelAnswer, documents: Sequence[str], state: AskState, deps: AskDeps
) -> Clarify:
    """Aday belgeler düğme olur: en az iki belge ve kapsam kullanıcı tarafından seçilmemişse.
    Üst sınır yok; aday sayısı zaten arama sonucu sayısıyla sınırlıdır."""
    show_choices = len(documents) >= _MIN_CLARIFY_DOCUMENTS and not state.request.doc_ids
    return Clarify(
        question=safe_clarify_question(
            answer.clarify.question if answer.clarify else "", state.question, state.language
        ),
        options=tuple(
            ClarifyChoice(doc_id=doc_id, label=deps.catalog.title(doc_id)) for doc_id in documents
        )
        if show_choices
        else (),
    )


def _without_repeats(items: Iterable[AnsweredItem]) -> tuple[AnsweredItem, ...]:
    """Model aynı doğrulanmış cümleyi tekrar yazarsa bir kez gösterilir; kaynakları birleşir.
    Tekrar cevabı başarısız saymaz: cümle doğrulanmıştır."""
    kept: list[AnsweredItem] = []
    first: dict[str, int] = {}
    for item in items:
        key = normalize(item.text)
        if not item.verified or key not in first:
            if item.verified:
                first[key] = len(kept)
            kept.append(item)
            continue
        earlier = kept[first[key]]
        known = {citation.chunk_id for citation in earlier.citations}
        added = tuple(c for c in item.citations if c.chunk_id not in known)
        kept[first[key]] = earlier.model_copy(update={"citations": (*earlier.citations, *added)})
    return tuple(kept)


async def verify(state: AskState, deps: AskDeps) -> AskState:
    assert state.answer is not None
    answer = state.answer
    sources = to_prompt_sources(state.hits, deps.catalog.language)
    verification = verify_answer(answer, sources, state.language, *user_text(state))
    if verification.status is VerificationStatus.NOT_FOUND:
        return replace(state, result=NotFound())
    if verification.status is VerificationStatus.CLARIFY:
        documents = _relevant_documents(
            candidate_documents(state.hits, verification.clarify_options), state, deps
        )
        asked, previous = user_text(state)
        agreed, cost = await agreed_answer(
            state.question,
            state.language,
            state.hits,
            documents,
            deps,
            _citation,
            asked=asked,
            previous=previous,
        )
        result = agreed or _clarification(answer, documents, state, deps)
        return replace(state, result=result, cost_usd=state.cost_usd + cost)
    if answer.kind is not AnswerKind.ANSWER:
        citations = tuple(_citation(hit) for hit in state.hits)
        return replace(state, result=Failed(reason=_MODEL_FAILED, citations=citations))
    checks = verification.items
    if checks and all(ABSENCE_CLAIM in check.problems for check in checks):
        # Cevabın tamamı "belgede yok" diyor: bu iddia yalnız "bulunamadı" olarak verilir.
        return replace(state, result=NotFound())
    items = _without_repeats(
        _answered_item(item, check, state.hits, sources)
        for item, check in zip(answer.items, verification.items, strict=True)
    )
    result = Answered(
        status=verification.status,
        items=items,
        has_conflict=answer.has_conflict,
        problems=verification.problems,
    )
    return replace(state, result=result)
