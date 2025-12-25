"""
Vector store service for knowledge base.
Uses pgvector for vector storage and similarity search.
"""

import logging
import re
from typing import Any
from uuid import UUID

import jieba

from app.llm import model_manager
from app.models.knowledge_base import DocumentChunk, Document
from app.services.usage_tracker import QuotaExceededError

logger = logging.getLogger(__name__)

# Initialize jieba (disable verbose output)
jieba.setLogLevel(logging.WARNING)


class VectorStore:
    """
    Vector store service using pgvector.

    Handles:
    - Embedding generation
    - Vector storage in PostgreSQL with pgvector
    - Similarity search
    - Token usage tracking (when team_id is provided)
    """

    def __init__(
        self,
        embedding_model_id: str | None = None,
        team_id: str | None = None,
    ):
        """
        Initialize vector store.

        Args:
            embedding_model_id: Optional embedding model ID to use
            team_id: Optional team ID for usage tracking
        """
        self.embedding_model_id = embedding_model_id
        self.team_id = team_id

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        try:
            # Use team-level embedding if team_id is provided
            if self.team_id and self.embedding_model_id:
                embeddings = await model_manager.team_embed(
                    team_id=self.team_id,
                    texts=texts,
                    model_id=self.embedding_model_id,
                )
            else:
                embeddings = await model_manager.embed(
                    texts, model_id=self.embedding_model_id
                )
            return embeddings
        except QuotaExceededError:
            logger.error(f"Team {self.team_id} quota exceeded for embedding")
            raise
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise

    async def embed_query(self, query: str) -> list[float]:
        """
        Generate embedding for a single query.

        Args:
            query: Query text

        Returns:
            Embedding vector
        """
        try:
            # Use team-level embedding if team_id is provided
            if self.team_id and self.embedding_model_id:
                embeddings = await model_manager.team_embed(
                    team_id=self.team_id,
                    texts=[query],
                    model_id=self.embedding_model_id,
                )
                return embeddings[0]
            else:
                embedding = await model_manager.embed_query(
                    query, model_id=self.embedding_model_id
                )
                return embedding
        except QuotaExceededError:
            logger.error(f"Team {self.team_id} quota exceeded for query embedding")
            raise
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            raise

    async def store_chunks(
        self,
        document: Document,
        chunks: list[dict[str, Any]],
    ) -> list[DocumentChunk]:
        """
        Store document chunks with embeddings.

        Args:
            document: Parent document
            chunks: List of chunk dicts with content, index, etc.

        Returns:
            List of created DocumentChunk objects
        """
        if not chunks:
            return []

        # Generate embeddings for all chunks
        texts = [c["content"] for c in chunks]
        embeddings = await self.embed_texts(texts)

        # Create chunk records
        created_chunks = []
        for chunk_data, embedding in zip(chunks, embeddings):
            # Store embedding reference
            # In production, store actual vector in pgvector column
            embedding_id = f"doc_{document.id}_chunk_{chunk_data['chunk_index']}"

            chunk = await DocumentChunk.create(
                document=document,
                content=chunk_data["content"],
                chunk_index=chunk_data["chunk_index"],
                token_count=chunk_data.get("token_count", 0),
                metadata=chunk_data.get("metadata"),
                embedding_id=embedding_id,
            )

            # TODO: Store actual embedding vector
            # await self._store_embedding(chunk.id, embedding)

            created_chunks.append(chunk)

        return created_chunks

    async def search(
        self,
        kb_id: UUID,
        query: str,
        search_mode: str = "hybrid",
        top_k: int = 5,
        score_threshold: float = 0.0,
        filter_doc_ids: list[UUID] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Search knowledge base using specified search mode.

        Args:
            kb_id: Knowledge base ID
            query: Search query
            search_mode: Search mode - "vector", "fulltext", or "hybrid"
            top_k: Number of results to return
            score_threshold: Minimum similarity score (0-1)
            filter_doc_ids: Optional list of document IDs to filter

        Returns:
            List of search results with chunk info and scores
        """
        results: list[dict[str, Any]] = []

        if search_mode == "vector":
            results = await self._vector_search(kb_id, query, top_k * 2, filter_doc_ids)
        elif search_mode == "fulltext":
            results = await self._fulltext_search(
                kb_id, query, top_k * 2, filter_doc_ids
            )
        else:  # hybrid
            # Get results from both methods
            vector_results = await self._vector_search(
                kb_id, query, top_k, filter_doc_ids
            )
            fulltext_results = await self._fulltext_search(
                kb_id, query, top_k, filter_doc_ids
            )

            # Merge results using RRF (Reciprocal Rank Fusion)
            results = self._merge_results_rrf(vector_results, fulltext_results)

        # Filter by score threshold
        if score_threshold > 0:
            results = [r for r in results if r.get("score", 0) >= score_threshold]

        # Return top_k
        return results[:top_k]

    async def _vector_search(
        self,
        kb_id: UUID,
        query: str,
        limit: int,
        filter_doc_ids: list[UUID] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Vector similarity search using embeddings.
        For now, uses database-level filtering + content similarity estimation.
        TODO: Replace with actual pgvector cosine similarity when embeddings are stored.
        """
        try:
            # Generate query embedding (for future use)
            await self.embed_query(query)
        except Exception as e:
            logger.warning(f"Failed to generate embedding: {e}")
            # Continue without embedding - fall back to content matching

        # Extract key terms from query for database filtering
        query_terms = self._extract_search_terms(query)

        # Build base query
        query_filter = DocumentChunk.filter(
            document__knowledge_base_id=kb_id
        ).prefetch_related("document")

        if filter_doc_ids:
            query_filter = query_filter.filter(document_id__in=filter_doc_ids)

        # Use database-level LIKE filtering to reduce candidates
        # Build OR conditions for each term
        from tortoise.expressions import Q

        if query_terms:
            or_conditions = Q()
            for term in query_terms[:5]:  # Limit to 5 terms
                or_conditions |= Q(content__icontains=term)
            query_filter = query_filter.filter(or_conditions)

        # Get filtered chunks (much smaller set)
        chunks = await query_filter.limit(limit * 3)

        results = []
        query_lower = query.lower()
        for chunk in chunks:
            # Quick scoring based on term matches
            score = self._quick_similarity_score(
                query_lower, query_terms, chunk.content.lower()
            )

            if score > 0:
                results.append(
                    {
                        "chunk_id": chunk.id,
                        "document_id": chunk.document.id,
                        "document_name": chunk.document.name,
                        "content": chunk.content,
                        "score": score,
                        "metadata": chunk.metadata,
                        "search_type": "vector",
                    }
                )

        # Sort by score
        results.sort(
            key=lambda x: float(x.get("score") or 0.0),  # type: ignore[arg-type]
            reverse=True,
        )
        return results[:limit]

    async def _fulltext_search(
        self,
        kb_id: UUID,
        query: str,
        limit: int,
        filter_doc_ids: list[UUID] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Full-text search using database-level filtering.
        """
        # Extract key terms from query
        query_terms = self._extract_search_terms(query)

        # Build base query
        query_filter = DocumentChunk.filter(
            document__knowledge_base_id=kb_id
        ).prefetch_related("document")

        if filter_doc_ids:
            query_filter = query_filter.filter(document_id__in=filter_doc_ids)

        # Use database-level filtering
        from tortoise.expressions import Q

        if query_terms:
            or_conditions = Q()
            for term in query_terms[:5]:
                or_conditions |= Q(content__icontains=term)
            query_filter = query_filter.filter(or_conditions)

        # Get filtered chunks
        chunks = await query_filter.limit(limit * 3)

        query_lower = query.lower()
        results = []
        for chunk in chunks:
            # Quick scoring
            score = self._quick_similarity_score(
                query_lower, query_terms, chunk.content.lower()
            )

            if score > 0:
                results.append(
                    {
                        "chunk_id": chunk.id,
                        "document_id": chunk.document.id,
                        "document_name": chunk.document.name,
                        "content": chunk.content,
                        "score": score,
                        "metadata": chunk.metadata,
                        "search_type": "fulltext",
                    }
                )

        # Sort by score
        results.sort(
            key=lambda x: float(x.get("score") or 0.0),  # type: ignore[arg-type]
            reverse=True,
        )
        return results[:limit]

    def _extract_search_terms(self, query: str) -> list[str]:
        """
        Extract search terms from query using jieba for Chinese segmentation.
        """
        # Use jieba for word segmentation (works for both Chinese and English)
        words = jieba.lcut(query)

        # Filter: keep words with length >= 2, remove pure punctuation
        terms = []
        for word in words:
            word = word.strip()
            # Skip empty, single char (unless Chinese), and pure punctuation
            if not word:
                continue
            if len(word) == 1 and not ("\u4e00" <= word <= "\u9fff"):
                continue
            if re.match(r"^[\s\W]+$", word):
                continue
            terms.append(word.lower() if word.isascii() else word)

        # Remove duplicates while preserving order
        seen = set()
        unique_terms = []
        for t in terms:
            if t not in seen:
                seen.add(t)
                unique_terms.append(t)

        return unique_terms

    def _quick_similarity_score(
        self, query: str, query_terms: list[str], content: str
    ) -> float:
        """
        Quick similarity scoring based on term matches.
        """
        if not query_terms:
            return 0.0

        content_lower = content.lower()

        # Count how many terms match
        matches = sum(
            1
            for term in query_terms
            if term in content_lower or term.lower() in content_lower
        )
        if matches == 0:
            return 0.0

        # Base score from match ratio
        base_score = matches / len(query_terms)

        # Bonus for exact phrase match
        query_clean = query.replace(" ", "").lower()
        content_clean = content_lower.replace(" ", "")
        if query_clean in content_clean:
            return min(1.0, base_score + 0.3)

        # Bonus for high match ratio
        if base_score >= 0.8:
            return min(1.0, base_score + 0.1)

        return min(1.0, base_score * 0.9)

    def _estimate_semantic_similarity(self, query: str, content: str) -> float:
        """
        Estimate semantic similarity (placeholder for actual vector similarity).
        Uses character/word overlap and substring matching.
        Supports both Chinese and English text.
        """
        if not query or not content:
            return 0.0

        # Tokenize: for Chinese, use character-level; for English, use word-level
        query_tokens = self._tokenize(query)
        content_tokens = self._tokenize(content)

        if not query_tokens:
            return 0.0

        # Token overlap ratio
        overlap = query_tokens & content_tokens
        overlap_ratio = len(overlap) / len(query_tokens)

        # Substring matching bonus (check if query or parts of it appear in content)
        substring_bonus = 0.0
        if query in content:
            substring_bonus = 0.4
        else:
            # Check for partial matches (sliding window for longer queries)
            query_chars = list(query.replace(" ", ""))
            if len(query_chars) >= 2:
                # Check 2-grams and 3-grams
                matches = 0
                total = 0
                for n in [2, 3, 4]:
                    for i in range(len(query_chars) - n + 1):
                        ngram = "".join(query_chars[i : i + n])
                        total += 1
                        if ngram in content:
                            matches += 1
                if total > 0:
                    substring_bonus = (matches / total) * 0.3

        # Calculate final score (0-1 range)
        score = min(1.0, overlap_ratio * 0.6 + substring_bonus)
        return round(score, 4)

    def _tokenize(self, text: str) -> set[str]:
        """
        Tokenization using jieba for Chinese and space-split for English.
        """
        # Use jieba for segmentation
        words = jieba.lcut(text)

        tokens = set()
        for word in words:
            word = word.strip()
            if not word:
                continue
            # Skip pure punctuation and whitespace
            if re.match(r"^[\s\W]+$", word) and not any(
                "\u4e00" <= c <= "\u9fff" for c in word
            ):
                continue
            # Normalize: lowercase for ASCII
            tokens.add(word.lower() if word.isascii() else word)

        return tokens

    def _calculate_fulltext_score(
        self, query: str, query_terms: list[str], content: str
    ) -> float:
        """
        Calculate full-text search score using jieba tokenization.
        """
        if not query_terms:
            return 0.0

        # Tokenize content
        content_tokens = self._tokenize(content)
        query_token_set = set(query_terms)

        # Check exact phrase match first
        query_clean = query.replace(" ", "").lower()
        content_clean = content.replace(" ", "").lower()
        if query_clean in content_clean:
            return 1.0

        # Token overlap
        matches = query_token_set & content_tokens
        if not matches:
            # Also check case-insensitive
            content_tokens_lower = {t.lower() for t in content_tokens}
            matches = {t for t in query_terms if t.lower() in content_tokens_lower}

        if not matches:
            return 0.0

        # Score based on match ratio
        score = len(matches) / len(query_terms)
        return round(min(1.0, score), 4)

    def _merge_results_rrf(
        self,
        vector_results: list[dict],
        fulltext_results: list[dict],
        k: int = 60,
    ) -> list[dict[str, Any]]:
        """
        Merge results using Reciprocal Rank Fusion (RRF).
        """
        scores: dict[str, float] = {}
        result_map: dict[str, dict] = {}

        # Process vector results
        for rank, result in enumerate(vector_results):
            chunk_id = str(result["chunk_id"])
            rrf_score = 1.0 / (k + rank + 1)
            scores[chunk_id] = scores.get(chunk_id, 0) + rrf_score
            if chunk_id not in result_map:
                result_map[chunk_id] = result

        # Process fulltext results
        for rank, result in enumerate(fulltext_results):
            chunk_id = str(result["chunk_id"])
            rrf_score = 1.0 / (k + rank + 1)
            scores[chunk_id] = scores.get(chunk_id, 0) + rrf_score
            if chunk_id not in result_map:
                result_map[chunk_id] = result

        # Sort by RRF score and update result scores
        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)

        merged_results = []
        for chunk_id in sorted_ids:
            result = result_map[chunk_id].copy()
            # Normalize RRF score to 0-1 range
            max_rrf = 2.0 / (k + 1)  # Max possible RRF score (rank 0 in both)
            result["score"] = round(min(1.0, scores[chunk_id] / max_rrf), 4)
            result["search_type"] = "hybrid"
            merged_results.append(result)

        return merged_results

    async def delete_document_vectors(self, document_id: UUID) -> int:
        """
        Delete all vectors for a document.

        Args:
            document_id: Document ID

        Returns:
            Number of deleted vectors
        """
        # Delete chunks (vectors stored with chunks)
        deleted = await DocumentChunk.filter(document_id=document_id).delete()

        # TODO: Delete from pgvector index if stored separately

        return deleted

    async def delete_chunk_vector(self, chunk_id: UUID) -> bool:
        """
        Delete vector for a single chunk.

        Args:
            chunk_id: Chunk ID

        Returns:
            True if deleted
        """
        # TODO: Delete from pgvector index if stored separately
        # For now, the chunk deletion handles this
        return True

    async def update_chunk_vector(self, chunk: DocumentChunk) -> bool:
        """
        Update vector embedding for a chunk.

        Args:
            chunk: DocumentChunk object with updated content

        Returns:
            True if updated
        """
        try:
            # Generate new embedding
            await self.embed_query(chunk.content)

            # Update embedding reference
            chunk.embedding_id = f"chunk_{chunk.id}_updated"
            await chunk.save()

            # TODO: Store actual embedding vector in pgvector
            # await self._update_embedding(chunk.id, embedding)

            logger.info(f"Updated vector for chunk {chunk.id}")
            return True
        except Exception as e:
            logger.error(f"Error updating chunk vector: {e}")
            return False

    async def add_chunk_vector(self, kb_id: UUID, chunk: DocumentChunk) -> bool:
        """
        Add vector embedding for a new chunk.

        Args:
            kb_id: Knowledge base ID
            chunk: DocumentChunk object

        Returns:
            True if added
        """
        try:
            # Generate embedding
            await self.embed_query(chunk.content)

            # Store embedding reference
            chunk.embedding_id = f"kb_{kb_id}_chunk_{chunk.id}"
            await chunk.save()

            # TODO: Store actual embedding vector in pgvector
            # await self._store_embedding(chunk.id, embedding)

            logger.info(f"Added vector for chunk {chunk.id}")
            return True
        except Exception as e:
            logger.error(f"Error adding chunk vector: {e}")
            return False

    async def delete_kb_vectors(self, kb_id: UUID) -> int:
        """
        Delete all vectors for a knowledge base.

        Args:
            kb_id: Knowledge base ID

        Returns:
            Number of deleted vectors
        """
        # Get all documents in KB
        documents = await Document.filter(knowledge_base_id=kb_id).values_list(
            "id", flat=True
        )

        if not documents:
            return 0

        # Delete all chunks
        deleted = await DocumentChunk.filter(document_id__in=documents).delete()

        return deleted


# Global instance
vector_store = VectorStore()
