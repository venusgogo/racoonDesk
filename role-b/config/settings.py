import os
from pathlib import Path

# ── Streamlit secrets / 환경변수 통합 읽기 ────────────────────
def _get_secret(key: str) -> str:
    if val := os.environ.get(key):
        return val
    try:
        import streamlit as st
        val = st.secrets.get(key, "")
        return val if val else ""
    except Exception:
        return ""

# ── API 키 ────────────────────────────────────────────────────
ANTHROPIC_API_KEY = _get_secret("ANTHROPIC_API_KEY")
OPENAI_API_KEY    = _get_secret("OPENAI_API_KEY")

# ── LLM 설정 ──────────────────────────────────────────────────
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")
MAX_TOKENS   = int(os.getenv("MAX_TOKENS", "2048"))

# ── 임베딩 설정 ───────────────────────────────────────────────
EMBEDDING_MODEL     = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_DIMENSION = 1536
CHUNK_SIZE          = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP       = int(os.getenv("CHUNK_OVERLAP", "100"))

# ── 검색 설정 ─────────────────────────────────────────────────
TOP_K                = int(os.getenv("TOP_K", "5"))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.3"))

# ── 경로 설정 ─────────────────────────────────────────────────
BASE_DIR         = Path(__file__).parent.parent
VECTOR_STORE_DIR = BASE_DIR / "data" / "vector_store"
VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)

FAISS_INDEX_PATH = str(VECTOR_STORE_DIR / "hr_regulations.faiss")
METADATA_PATH    = str(VECTOR_STORE_DIR / "hr_regulations_meta.json")
