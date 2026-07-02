"""ChromaDB vector store — uses Chroma Cloud on Vercel, local PersistentClient in dev."""

from typing import Any

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import settings
from app.rag.chunker import chunk_text
from app.rag.embeddings import embed_query, embed_texts

COLLECTION_NAME = "studymate_documents"


def _make_chroma_client() -> chromadb.ClientAPI:
    """Return a Chroma Cloud client if credentials are set, else local persistent client."""
    if settings.use_chroma_cloud:
        return chromadb.HttpClient(
            host="api.trychroma.com",
            ssl=True,
            port=443,
            headers={"x-chroma-token": settings.chroma_api_key},
            tenant=settings.chroma_tenant,
            database=settings.chroma_database,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
    # Local development fallback
    return chromadb.PersistentClient(
        path=str(settings.chroma_path),
        settings=ChromaSettings(anonymized_telemetry=False),
    )


class VectorStore:
    """Manages document chunks in ChromaDB for semantic search."""

    def __init__(self) -> None:
        self._client = _make_chroma_client()
        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    def add_document(
        self,
        document_id: int,
        text: str,
        metadata: dict[str, Any] | None = None,
    ) -> int:
        """Chunk, embed, and store a document. Returns number of chunks stored."""
        chunks = chunk_text(text)
        if not chunks:
            return 0

        embeddings = embed_texts(chunks)
        ids = [f"doc_{document_id}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [
            {
                "document_id": document_id,
                "chunk_index": i,
                **(metadata or {}),
            }
            for i in range(len(chunks))
        ]

        self._collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
        )
        return len(chunks)

    def search(
        self,
        query: str,
        document_id: int | None = None,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Semantic search over stored document chunks."""
        if self._collection.count() == 0:
            return []

        query_embedding = embed_query(query)
        where_filter = {"document_id": document_id} if document_id is not None else None

        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, self._collection.count()),
            where=where_filter,
        )

        chunks: list[dict[str, Any]] = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                chunks.append(
                    {
                        "text": doc,
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": results["distances"][0][i] if results["distances"] else 0.0,
                    }
                )
        return chunks

    def delete_document(self, document_id: int) -> None:
        """Remove all chunks for a document."""
        try:
            self._collection.delete(where={"document_id": document_id})
        except Exception:
            pass

    def get_document_chunks(self, document_id: int) -> list[str]:
        """Retrieve all chunks for a document."""
        results = self._collection.get(where={"document_id": document_id})
        if results and results["documents"]:
            return results["documents"]
        return []

    @property
    def total_chunks(self) -> int:
        return self._collection.count()


_vector_store: VectorStore | None = None


def get_vector_store() -> VectorStore:
    """Singleton accessor for the vector store."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
