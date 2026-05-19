import json
import numpy as np
import faiss
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from config.settings import (
    FAISS_INDEX_PATH,
    METADATA_PATH,
    TOP_K,
    SIMILARITY_THRESHOLD,
)
from rag.loader import Chunk
from rag.embedder import Embedder


@dataclass
class SearchResult:
    chunk: Chunk
    score: float          # 코사인 유사도 (0~1)
    rank: int


class Retriever:
    def __init__(
        self,
        embedder: Optional[Embedder] = None,
        index_path: str = FAISS_INDEX_PATH,
        metadata_path: str = METADATA_PATH,
    ):
        self.embedder = embedder or Embedder()
        self.index_path = index_path
        self.metadata_path = metadata_path

        self._index: Optional[faiss.IndexFlatIP] = None
        self._chunks: list[Chunk] = []

    # ------------------------------------------------------------------ #
    # 인덱스 구축                                                           #
    # ------------------------------------------------------------------ #

    def build_index(self, chunks: list[Chunk]) -> None:
        """청크 목록으로 FAISS 인덱스를 구축합니다."""
        if not chunks:
            raise ValueError("청크가 비어 있습니다.")

        embeddings = self.embedder.embed_chunks(chunks)
        # 코사인 유사도를 위해 L2 정규화
        faiss.normalize_L2(embeddings)

        dimension = embeddings.shape[1]
        self._index = faiss.IndexFlatIP(dimension)   # Inner Product == cosine after normalization
        self._index.add(embeddings)
        self._chunks = chunks

    def save(self) -> None:
        if self._index is None:
            raise RuntimeError("인덱스가 비어 있습니다. build_index()를 먼저 호출하세요.")

        faiss.write_index(self._index, self.index_path)
        metadata = [
            {"chunk_id": c.chunk_id, "text": c.text, "metadata": c.metadata}
            for c in self._chunks
        ]
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

    def load(self) -> bool:
        """저장된 인덱스를 로드합니다. 성공 여부를 반환합니다."""
        if not Path(self.index_path).exists() or not Path(self.metadata_path).exists():
            return False

        self._index = faiss.read_index(self.index_path)
        with open(self.metadata_path, encoding="utf-8") as f:
            data = json.load(f)
        self._chunks = [
            Chunk(text=d["text"], metadata=d["metadata"], chunk_id=d["chunk_id"])
            for d in data
        ]
        return True

    # ------------------------------------------------------------------ #
    # 검색                                                                 #
    # ------------------------------------------------------------------ #

    def search(
        self,
        query: str,
        top_k: int = TOP_K,
        threshold: float = SIMILARITY_THRESHOLD,
    ) -> list[SearchResult]:
        if self._index is None:
            raise RuntimeError("인덱스가 로드되지 않았습니다.")

        query_vec = self.embedder.embed_query(query).reshape(1, -1)
        faiss.normalize_L2(query_vec)

        scores, indices = self._index.search(query_vec, min(top_k, len(self._chunks)))
        scores, indices = scores[0], indices[0]

        results: list[SearchResult] = []
        for rank, (idx, score) in enumerate(zip(indices, scores), start=1):
            if idx == -1:
                continue
            if float(score) < threshold:
                continue
            results.append(
                SearchResult(
                    chunk=self._chunks[idx],
                    score=float(score),
                    rank=rank,
                )
            )

        return results

    # ------------------------------------------------------------------ #
    # 유틸                                                                  #
    # ------------------------------------------------------------------ #

    @property
    def is_ready(self) -> bool:
        return self._index is not None and len(self._chunks) > 0

    @property
    def chunk_count(self) -> int:
        return len(self._chunks)

    def get_unique_articles(self, results: list[SearchResult]) -> list[str]:
        """검색 결과에서 중복 없는 조항 번호 목록을 반환합니다."""
        seen: set[str] = set()
        articles: list[str] = []
        for r in results:
            article = r.chunk.metadata.get("article")
            if article and article not in seen:
                seen.add(article)
                articles.append(article)
        return articles
