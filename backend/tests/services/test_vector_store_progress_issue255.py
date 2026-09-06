from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest

from app.services.vector_store import VectorStore

vector_store_module = pytest.importorskip("app.services.vector_store")


@pytest.fixture(autouse=True)
def fake_transaction(monkeypatch):
    @asynccontextmanager
    async def transaction():
        yield object()

    monkeypatch.setattr(vector_store_module, "in_transaction", transaction)


class FakeDocumentChunk:
    created = []

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", uuid4())
        self.save = AsyncMock()
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    async def bulk_create(cls, chunks, using_db=None):
        cls.created.extend(chunks)

    @classmethod
    async def bulk_update(cls, chunks, fields, using_db=None):
        return None


@pytest.fixture(autouse=True)
def fake_document_chunk(monkeypatch):
    FakeDocumentChunk.created = []
    monkeypatch.setattr(vector_store_module, "DocumentChunk", FakeDocumentChunk)


@pytest.fixture
def document():
    return SimpleNamespace(
        id=UUID("00000000-0000-0000-0000-000000000010"),
        knowledge_base_id=UUID("00000000-0000-0000-0000-000000000001"),
    )


@pytest.mark.asyncio
async def test_store_chunks_with_progress_returns_empty_without_work(document):
    calls = []

    result = await VectorStore().store_chunks_with_progress(
        document,
        [],
        progress_callback=lambda *args: calls.append(args),
    )

    assert result == []
    assert calls == []
    assert FakeDocumentChunk.created == []


@pytest.mark.asyncio
async def test_store_chunks_with_progress_embeds_each_chunk(monkeypatch, document):
    progress = []
    ensured = []

    async def fake_embed_texts(self, texts):
        return [[float(len(texts[0])), 0.2]]

    async def fake_ensure_kb_dimension(kb_id, dimension):
        ensured.append((kb_id, dimension))

    async def fake_progress(embedded, failed, total):
        progress.append((embedded, failed, total))

    batch_store = AsyncMock()

    monkeypatch.setattr(VectorStore, "embed_texts", fake_embed_texts)
    monkeypatch.setattr(VectorStore, "_batch_store_embeddings", batch_store)
    monkeypatch.setattr(
        vector_store_module, "_ensure_kb_dimension", fake_ensure_kb_dimension
    )

    chunks = [
        {"content": "alpha", "chunk_index": 0, "token_count": 2, "metadata": {"p": 1}},
        {"content": "beta", "chunk_index": 1},
    ]

    result = await VectorStore().store_chunks_with_progress(
        document,
        chunks,
        progress_callback=fake_progress,
        batch_size=1,
    )

    assert result == FakeDocumentChunk.created
    assert [chunk.status for chunk in result] == ["embedded", "embedded"]
    assert [chunk.error_message for chunk in result] == [None, None]
    assert ensured == [
        (document.knowledge_base_id, 2),
        (document.knowledge_base_id, 2),
    ]
    assert batch_store.await_count == 2
    for chunk in result:
        assert chunk.save.await_count == 0


@pytest.mark.asyncio
async def test_store_chunks_with_progress_marks_failed_chunk(monkeypatch, document):
    progress = []

    async def fake_embed_texts(self, texts):
        if texts == ["bad"]:
            raise RuntimeError("embedding failed")
        return [[0.1, 0.2, 0.3]]

    async def fake_ensure_kb_dimension(kb_id, dimension):
        assert kb_id == document.knowledge_base_id
        assert dimension == 3

    async def fake_store_embedding(
        self, chunk_id, embedding, dimension=None, payload=None
    ):
        assert embedding == [0.1, 0.2, 0.3]
        assert dimension == 3

    async def fake_progress(embedded, failed, total):
        progress.append((embedded, failed, total))

    monkeypatch.setattr(VectorStore, "embed_texts", fake_embed_texts)
    monkeypatch.setattr(VectorStore, "_store_embedding", fake_store_embedding)
    monkeypatch.setattr(
        vector_store_module, "_ensure_kb_dimension", fake_ensure_kb_dimension
    )

    result = await VectorStore().store_chunks_with_progress(
        document,
        [
            {"content": "bad", "chunk_index": 0},
            {"content": "good", "chunk_index": 1},
        ],
        progress_callback=fake_progress,
    )

    assert [chunk.status for chunk in result] == ["failed", "embedded"]
    assert result[0].error_message == "document_process_failed"
    assert progress == [(1, 1, 2)]
