import os

# LLM 설정
LLM_MODEL = "claude-sonnet-4-6"
LLM_MAX_TOKENS = 1024
LLM_TEMPERATURE = 0.0  # 규정 답변은 일관성 우선

# 임베딩 설정
EMBEDDING_MODEL = "text-embedding-3-small"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# 검색 설정
TOP_K = 5  # 검색할 유사 청크 수

# 경로 설정
DATA_DIR = os.path.join(os.path.dirname(__file__), "../../role-a/data/processed")
VECTORSTORE_DIR = os.path.join(os.path.dirname(__file__), "../rag/vectorstore")

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
