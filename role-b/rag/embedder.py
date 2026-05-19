import json
import numpy as np
from typing import Optional
from openai import OpenAI

from config.settings import OPENAI_API_KEY, EMBEDDING_MODEL, EMBEDDING_DIMENSION
from rag.loader import Chunk


class Embedder:
    def __init__(self, model: str = EMBEDDING_MODEL, api_key: Optional[str] = None):
        self.model = model
        key = api_key or OPENAI_API_KEY
        if not key:
            raise EnvironmentError(
                "OPENAI_API_KEY가 설정되지 않았습니다. "
                "Streamlit Cloud → App settings → Secrets에 OPENAI_API_KEY를 추가하세요."
            )
        self.client = OpenAI(api_key=key)
        self.dimension = EMBEDDING_DIMENSION

    def embed_texts(self, texts: list[str], batch_size: int = 100) -> np.ndarray:
        """텍스트 목록을 임베딩 행렬로 변환합니다."""
        all_embeddings: list[list[float]] = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            # 빈 텍스트 방지
            batch = [t if t.strip() else " " for t in batch]
            response = self.client.embeddings.create(model=self.model, input=batch)
            batch_embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(batch_embeddings)

        return np.array(all_embeddings, dtype=np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        """단일 쿼리를 임베딩 벡터로 변환합니다."""
        response = self.client.embeddings.create(model=self.model, input=[query])
        return np.array(response.data[0].embedding, dtype=np.float32)

    def embed_chunks(self, chunks: list[Chunk], batch_size: int = 100) -> np.ndarray:
        """Chunk 목록을 임베딩 행렬로 변환합니다."""
        texts = [c.text for c in chunks]
        return self.embed_texts(texts, batch_size=batch_size)
