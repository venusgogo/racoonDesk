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


# ── API 키 (선택사항) ─────────────────────────────────────────
# GEMINI_API_KEY가 없으면 검색 전용 모드로 동작합니다.
GEMINI_API_KEY = _get_secret("GEMINI_API_KEY")

# ── LLM 설정 ──────────────────────────────────────────────────
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# ── 로컬 임베딩 설정 (API 키 불필요) ──────────────────────────
# jhgan/ko-sroberta-multitask: 한국어 특화 sentence-transformers 모델
EMBEDDING_MODEL_LOCAL     = os.getenv("EMBEDDING_MODEL_LOCAL", "jhgan/ko-sroberta-multitask")
EMBEDDING_DIMENSION_LOCAL = 768

# ── 검색 설정 ─────────────────────────────────────────────────
TOP_K                = int(os.getenv("TOP_K", "5"))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.3"))

# ── 청킹 설정 ─────────────────────────────────────────────────
CHUNK_SIZE    = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))

# ── 경로 설정 ─────────────────────────────────────────────────
BASE_DIR         = Path(__file__).parent.parent
VECTOR_STORE_DIR = BASE_DIR / "data" / "vector_store"
VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)

FAISS_INDEX_PATH = str(VECTOR_STORE_DIR / "hr_regulations.faiss")
METADATA_PATH    = str(VECTOR_STORE_DIR / "hr_regulations_meta.json")

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
