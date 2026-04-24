from typing import List, Dict, Tuple
import numpy as np
import faiss
from openai import OpenAI

from config.settings import EMBEDDING_MODEL, TOP_K


client = OpenAI()


def retrieve(query: str, index: faiss.Index, chunks: List[Dict], top_k: int = TOP_K) -> List[Dict]:
    """질문과 가장 유사한 조항 청크를 검색합니다."""
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=[query])
    query_vector = np.array([response.data[0].embedding], dtype="float32")

    distances, indices = index.search(query_vector, top_k)

    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx == -1:
            continue
        chunk = chunks[idx].copy()
        chunk["score"] = float(dist)
        results.append(chunk)

    return results
