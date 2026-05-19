import os

# LLM 설정
CLAUDE_MODEL   = "claude-sonnet-4-6"
MAX_TOKENS     = 1024
LLM_TEMPERATURE = 0.0

# 임베딩 설정
EMBEDDING_MODEL     = "text-embedding-3-small"
EMBEDDING_DIMENSION = 1536
CHUNK_SIZE          = 500
CHUNK_OVERLAP       = 50

# 검색 설정
TOP_K                = 5
SIMILARITY_THRESHOLD = 0.3

# 경로 설정
DATA_DIR          = os.path.join(os.path.dirname(__file__), "../../role-a/data/processed")
FAISS_INDEX_PATH  = os.path.join(os.path.dirname(__file__), "../rag/vectorstore/index.faiss")
METADATA_PATH     = os.path.join(os.path.dirname(__file__), "../rag/vectorstore/chunks.json")

# API 키 — 환경변수 우선, 없으면 Streamlit secrets fallback
def _get_secret(key: str) -> str:
    if val := os.environ.get(key):
        return val
    try:
        import streamlit as st
        return st.secrets.get(key, "")
    except Exception:
        return ""

ANTHROPIC_API_KEY = _get_secret("ANTHROPIC_API_KEY")
OPENAI_API_KEY    = _get_secret("OPENAI_API_KEY")
