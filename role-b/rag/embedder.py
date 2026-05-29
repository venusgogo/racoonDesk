import numpy as np
from typing import Optional
from sentence_transformers import SentenceTransformer

from config.settings import EMBEDDING_MODEL_LOCAL, EMBEDDING_DIMENSION_LOCAL
from rag.loader import Chunk


class Embedder:
    """
    sentence-transformers 기반 로컬 임베더.
    API 키 없이 무료로 동작합니다.
    기본 모델: jhgan/ko-sroberta-multitask (한국어 특화)
    """

    def __init__(self, model: str = EMBEDDING_MODEL_LOCAL):
        self.model_name = model
        self._model: Optional[SentenceTransformer] = None
        self.dimension = EMBEDDING_DIMENSION_LOCAL

    @property
    def _st_model(self) -> SentenceTransformer:
        """지연 로딩 - 처음 호출 시에만 모델을 다운로드합니다."""
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed_texts(self, texts: list[str], batch_size: int = 32) -> np.ndarray:
        """텍스트 목록을 임베딩 행렬로 변환합니다."""
        texts = [t if t.strip() else " " for t in texts]
        embeddings = self._st_model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=False,
            convert_to_numpy=True,
        )
        return np.array(embeddings, dtype=np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        """단일 쿼리를 임베딩 벡터로 변환합니다."""
        embedding = self._st_model.encode(
            [query],
            show_progress_bar=False,
            convert_to_numpy=True,
        )
        return np.array(embedding[0], dtype=np.float32)

    def embed_chunks(self, chunks: list[Chunk], batch_size: int = 32) -> np.ndarray:
        """Chunk 목록을 임베딩 행렬로 변환합니다."""
        texts = [c.text for c in chunks]
        return self.embed_texts(texts, batch_size=batch_size)
