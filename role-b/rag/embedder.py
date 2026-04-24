import os
import pickle
from typing import List, Dict
import faiss
import numpy as np
from openai import OpenAI

from config.settings import EMBEDDING_MODEL, VECTORSTORE_DIR


client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))


def embed_texts(texts: List[str]) -> np.ndarray:
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
    return np.array([item.embedding for item in response.data], dtype="float32")


def build_vectorstore(chunks: List[Dict], save_path: str = VECTORSTORE_DIR) -> faiss.Index:
    os.makedirs(save_path, exist_ok=True)

    texts = [c["content"] for c in chunks]
    vectors = embed_texts(texts)

    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)

    faiss.write_index(index, os.path.join(save_path, "index.faiss"))
    with open(os.path.join(save_path, "chunks.pkl"), "wb") as f:
        pickle.dump(chunks, f)

    return index


def load_vectorstore(save_path: str = VECTORSTORE_DIR):
    index = faiss.read_index(os.path.join(save_path, "index.faiss"))
    with open(os.path.join(save_path, "chunks.pkl"), "rb") as f:
        chunks = pickle.load(f)
    return index, chunks
