"""Ölçümlerin ortak parça önbelleği ve indeksi.

Parçalar --work altında saklanır, belge işleme yeniden yapılmaz. Vektörler parçalar
değişmedikçe yeniden üretilmez: indeks, parçaların parmak iziyle işaretlenir.
"""

import hashlib
import json
import sys
import tempfile
import time
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from visual_agent.domain.document import Chunk, DocumentMeta
from visual_agent.retrieval.qdrant_store import QdrantChunkStore
from visual_agent.settings import Settings

_EMBED_BATCH = 256
_CHUNKS_FILE = "chunks.json"
_INGEST_FILE = "ingest.json"
_INDEX_FILE = "index.json"

Documents = Sequence[tuple[Path, DocumentMeta]]


def chunks_fingerprint(chunks: Sequence[Chunk]) -> str:
    digest = hashlib.sha256()
    for chunk in chunks:
        digest.update(chunk.chunk_id.encode("utf-8"))
        digest.update(chunk.embed_text.encode("utf-8"))
    return digest.hexdigest()


def _ingest_all(documents: Documents) -> tuple[dict[str, list[Chunk]], dict[str, Any]]:
    """Belgeler uygulamanın işleme koduyla işlenir; tek belgedeki hata ötekileri durdurmaz.

    Manifest: belge ve parça sayısı, toplam süre, hatalar ve belge başına süre ile rapor.
    """
    from visual_agent.ingest.external import locate_tools
    from visual_agent.ingest.pipeline import ingest_document
    from visual_agent.ingest.tools import default_tools

    settings = Settings()
    tools = default_tools(locate_tools(settings.soffice_path, settings.tesseract_path))
    chunks: dict[str, list[Chunk]] = {}
    errors: dict[str, str] = {}
    per_document: dict[str, dict[str, Any]] = {}
    started = time.perf_counter()
    for path, meta in documents:
        begun = time.perf_counter()
        try:
            with tempfile.TemporaryDirectory() as work:
                result = ingest_document(path, meta, tools, Path(work))
        except Exception as error:
            errors[meta.doc_id] = f"{type(error).__name__}: {error}"
            continue
        chunks[meta.doc_id] = list(result.chunks)
        per_document[meta.doc_id] = {
            "seconds": round(time.perf_counter() - begun, 1),
            "report": result.report.model_dump(mode="json"),
        }
    manifest = {
        "files": len(chunks) + len(errors),
        "documents": len(chunks),
        "chunks": sum(len(items) for items in chunks.values()),
        "ingest_seconds": round(time.perf_counter() - started, 1),
        "errors": errors,
        "per_document": per_document,
    }
    return chunks, manifest


def read_chunks(work: Path) -> dict[str, list[Chunk]] | None:
    """Var olan parça önbelleği; yoksa None. Hiçbir şey yazmaz."""
    cache = work / _CHUNKS_FILE
    if not cache.exists():
        return None
    raw = json.loads(cache.read_text(encoding="utf-8"))
    return {doc: [Chunk.model_validate(item) for item in items] for doc, items in raw.items()}


def load_or_ingest(
    documents: Documents, work: Path, keep_partial: bool = True
) -> tuple[dict[str, list[Chunk]], dict[str, Any]]:
    """Parça önbelleği varsa okunur; yoksa belgeler işlenir. Hatalar raporda döner.

    keep_partial=False: işlenemeyen belge varsa önbellek yazılmaz; sonraki koşu yeniden dener.
    """
    manifest_path = work / _INGEST_FILE
    cached = read_chunks(work)
    if cached is not None:
        manifest = (
            json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
        )
        return cached, manifest
    chunks, manifest = _ingest_all(documents)
    if manifest["errors"] and not keep_partial:
        return chunks, manifest
    payload = {doc: [c.model_dump(mode="json") for c in items] for doc, items in chunks.items()}
    (work / _CHUNKS_FILE).write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    return chunks, manifest


async def ensure_index(
    flat: Sequence[Chunk], dense: Any, sparse: Any, store: QdrantChunkStore, work: Path
) -> dict[str, Any]:
    """Vektörler parçalar değişmedikçe yeniden üretilmez."""
    marker = work / _INDEX_FILE
    fingerprint = chunks_fingerprint(flat)
    if marker.exists():
        saved = json.loads(marker.read_text(encoding="utf-8"))
        if saved.get("fingerprint") == fingerprint:
            return dict(saved)
    await store.recreate_collection(dense.size)
    started = time.perf_counter()
    for start in range(0, len(flat), _EMBED_BATCH):
        batch = list(flat[start : start + _EMBED_BATCH])
        texts = [chunk.embed_text for chunk in batch]
        await store.upsert(
            batch, ("all",), dense.encode_documents(texts), sparse.encode_documents(texts)
        )
        print(f"vektör: {start + len(batch)}/{len(flat)}", file=sys.stderr, flush=True)
    saved = {
        "fingerprint": fingerprint,
        "chunks": len(flat),
        "embed_seconds": round(time.perf_counter() - started, 1),
    }
    marker.write_text(json.dumps(saved, indent=1), encoding="utf-8")
    return saved
