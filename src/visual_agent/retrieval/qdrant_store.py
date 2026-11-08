"""Parçaların Qdrant'ta saklanması ve iki kollu arama."""

import uuid
from collections.abc import Mapping, Sequence

from qdrant_client import AsyncQdrantClient, models

from visual_agent.domain.document import Chunk
from visual_agent.retrieval.fusion import ScoredChunk

_DENSE = "dense"
_SPARSE = "bm25"
_POINT_NAMESPACE = uuid.UUID("7a1e9d10-3f5b-4a54-9c0e-0d3b2f6a8c11")
_ACCESS_ALL = "all"
_UPSERT_BATCH = 64

SparseVector = Mapping[int, float]


def _point_id(chunk_id: str) -> str:
    return str(uuid.uuid5(_POINT_NAMESPACE, chunk_id))


def _filter(doc_ids: Sequence[str] | None, access: Sequence[str] | None) -> models.Filter | None:
    conditions: list[models.Condition] = []
    if doc_ids is not None:
        conditions.append(
            models.FieldCondition(key="doc_id", match=models.MatchAny(any=list(doc_ids)))
        )
    if access is not None:
        allowed = sorted({*access, _ACCESS_ALL})
        conditions.append(models.FieldCondition(key="access", match=models.MatchAny(any=allowed)))
    return models.Filter(must=conditions) if conditions else None


def _sparse_vector(values: SparseVector) -> models.SparseVector:
    return models.SparseVector(indices=list(values.keys()), values=list(values.values()))


def _to_scored(points: Sequence[models.ScoredPoint]) -> list[ScoredChunk]:
    scored = [
        ScoredChunk(Chunk.model_validate((point.payload or {})["chunk"]), point.score)
        for point in points
    ]
    return sorted(scored, key=lambda item: (-item.score, item.chunk.chunk_id))


class QdrantChunkStore:
    def __init__(self, client: AsyncQdrantClient, collection: str) -> None:
        self._client = client
        self._collection = collection

    async def ensure_collection(self, dense_size: int) -> None:
        if await self._client.collection_exists(self._collection):
            return
        await self._client.create_collection(
            self._collection,
            vectors_config={
                _DENSE: models.VectorParams(size=dense_size, distance=models.Distance.COSINE)
            },
            sparse_vectors_config={
                _SPARSE: models.SparseVectorParams(modifier=models.Modifier.IDF)
            },
        )

    async def recreate_collection(self, dense_size: int) -> None:
        await self._client.delete_collection(self._collection)
        await self.ensure_collection(dense_size)

    async def upsert(
        self,
        chunks: Sequence[Chunk],
        access: Sequence[str],
        dense: Sequence[Sequence[float]],
        sparse: Sequence[SparseVector],
    ) -> None:
        points = [
            models.PointStruct(
                id=_point_id(chunk.chunk_id),
                vector={_DENSE: list(dense_vector), _SPARSE: _sparse_vector(sparse_vector)},
                payload={
                    "doc_id": chunk.doc_id,
                    "access": list(access),
                    "chunk": chunk.model_dump(mode="json"),
                },
            )
            for chunk, dense_vector, sparse_vector in zip(chunks, dense, sparse, strict=True)
        ]
        for start in range(0, len(points), _UPSERT_BATCH):
            await self._client.upsert(self._collection, points[start : start + _UPSERT_BATCH])

    async def delete_document(self, doc_id: str) -> None:
        await self._client.delete(
            self._collection,
            points_selector=models.FilterSelector(filter=_filter((doc_id,), None)),
        )

    async def search(
        self,
        dense: Sequence[float],
        sparse: SparseVector,
        doc_ids: Sequence[str] | None,
        access: Sequence[str] | None,
        limit: int,
    ) -> list[list[ScoredChunk]]:
        """Yetki koşulu sorgunun içindedir: yetkisiz parça hiçbir kola girmez."""
        condition = _filter(doc_ids, access)
        requests = [
            models.QueryRequest(
                query=list(dense), using=_DENSE, filter=condition, limit=limit, with_payload=True
            )
        ]
        if sparse:
            requests.append(
                models.QueryRequest(
                    query=_sparse_vector(sparse),
                    using=_SPARSE,
                    filter=condition,
                    limit=limit,
                    with_payload=True,
                )
            )
        responses = await self._client.query_batch_points(self._collection, requests=requests)
        arms = [_to_scored(response.points) for response in responses]
        return arms if len(arms) == 2 else [*arms, []]
