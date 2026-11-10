"""Belge silme: önce kayıt gizlenir, sonra vektörler ve dosyalar, en son kayıt kalkar.

Kayıt ilk adımda "siliniyor" olur; belge listeden, katalogdan ve aramadan hemen çıkar.
Vektör ya da dosya temizliği başarısız olursa kayıt o durumda kalır ve açılışta yeniden
denenir; belge bu arada hiçbir yerde görünmez.
"""

import asyncio
import logging
import shutil
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Protocol

from visual_agent.catalog.repository import StoredDocument

logger = logging.getLogger(__name__)

RemoveVectors = Callable[[str], Awaitable[None]]


class DeletionRepository(Protocol):
    async def mark_deleting(self, doc_id: str) -> StoredDocument | None: ...

    async def deleting_documents(self) -> list[StoredDocument]: ...

    async def purge(self, doc_id: str) -> None: ...


def document_directory(storage: Path, doc_id: str) -> Path:
    """Belgenin dosyaları depolama klasöründeki kendi klasöründedir; dışına çıkılmaz."""
    directory = (storage / doc_id).resolve()
    if directory.parent != storage.resolve() or not doc_id:
        raise ValueError(f"geçersiz belge kimliği: {doc_id!r}")
    return directory


async def _remove_files(storage: Path, doc_id: str) -> None:
    directory = document_directory(storage, doc_id)
    if directory.exists():
        await asyncio.to_thread(shutil.rmtree, directory)


async def finish_deletion(
    document: StoredDocument,
    repository: DeletionRepository,
    remove_vectors: RemoveVectors,
    storage: Path,
) -> bool:
    """Her temizlik adımı ayrı denenir; hepsi başarılıysa kayıt kalkar."""
    complete = True
    try:
        await remove_vectors(document.doc_id)
    except Exception:
        logger.warning("Vektörler silinemedi, açılışta yeniden denenecek: %s", document.doc_id)
        complete = False
    try:
        await _remove_files(storage, document.doc_id)
    except OSError:
        logger.warning("Dosyalar silinemedi, açılışta yeniden denenecek: %s", document.doc_id)
        complete = False
    if complete:
        await repository.purge(document.doc_id)
    return complete


async def delete_document(
    doc_id: str,
    repository: DeletionRepository,
    remove_vectors: RemoveVectors,
    storage: Path,
) -> bool:
    """Belge yoksa False; varsa temizlik yarım kalsa bile belge artık görünmez."""
    document = await repository.mark_deleting(doc_id)
    if document is None:
        return False
    await finish_deletion(document, repository, remove_vectors, storage)
    return True


async def retry_deletions(
    repository: DeletionRepository, remove_vectors: RemoveVectors, storage: Path
) -> int:
    """Yarım kalan silmeleri tamamlar; tamamlanan sayısını döndürür."""
    finished = 0
    for document in await repository.deleting_documents():
        finished += await finish_deletion(document, repository, remove_vectors, storage)
    return finished
