import sys
import os
import time

ROLE_C_DIR = os.path.join(os.path.dirname(__file__), "..")
REPO_ROOT   = os.path.join(os.path.dirname(__file__), "../..")
sys.path.insert(0, ROLE_C_DIR)
sys.path.insert(0, REPO_ROOT)

import streamlit as st

from ui.components.feedback_widget import render_feedback_widget, render_feedback_summary
from ui.components.metrics_dashboard import render_dashboard, log_query
from ui.components.onboarding import render_onboarding

# Role B RAG 엔진 연결 (새 클래스 기반 API)
try:
    sys.path.insert(0, os.path.join(REPO_ROOT, "role-b"))
    from rag.loader import DocumentLoader
    from rag.embedder import Embedder
    from rag.retriever import Retriever
    from rag.generator import Generator
    RAG_AVAILABLE = True
except Exception:
    RAG_AVAILABLE = False

# ── 페이지 설정 ──────────────────────────────────────────────
st.set_page_config(
    page_title="RACOON Desk",
    page_icon="🦝",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS 로드 ─────────────────────────────────────────────────
css_path = os.path.join(os.path.dirname(__file__), "../ui/styles/racoon_theme.css")
if os.path.exists(css_path):
    with open(css_path, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── RAG 컴포넌트 캐싱 ─────────────────────────────────────────
@st.cache_resource
def get_rag_components():
    embedder  = Embedder()
    retriever = Retriever(embedder=embedder)
    generator = Generator()
    loader    = DocumentLoader()
    retriever.load()
    return loader, retriever, generator

# ── 헤더 ─────────────────────────────────────────────────────
st.markdown("""
<div class="racoon-header">
  <div>
    <h1>🦝 RACOON Desk</h1>
    <p>인사관리 규정 AI 질의응답 시스템</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ── 사이드바 ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 메뉴")
    page = st.radio(
        "",
        ["💬 질의응답", "📖 사용 가이드", "📊 사용 현황"],
        label_visibility="collapsed",
    )

    st.divider()

    if RAG_AVAILABLE:
        st.markdown("### 규정 파일 관리")
        uploaded = st.file_uploader(
            "파일 업로드 (MD / TXT / PDF / DOCX)",
            type=["md", "txt", "pdf", "docx"],
        )
        if uploaded:
            import tempfile, pathlib
            suffix = pathlib.Path(uploaded.name).suffix
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded.read())
                tmp_path = tmp.name

            _, retriever, _ = get_rag_components()
            loader = DocumentLoader()
            chunks = loader.load(tmp_path)
            st.info(f"조항 {len(chunks)}개 감지됨")

            if st.button("⚙️ 인덱스 구축", type="primary", use_container_width=True):
                with st.spinner("학습 중..."):
                    retriever.build_index(chunks)
                    retriever.save()
                    st.cache_resource.clear()
                st.success("완료!")
    else:
        st.warning("RAG 모듈을 불러올 수 없습니다.\nAPI 키와 패키지를 확인하세요.")

    st.divider()
    st.markdown("### 피드백 현황")
    render_feedback_summary()
    st.divider()
    st.caption("RACOON Desk v1.0 · Role C UX")

# ── 페이지 라우팅 ──────────────────────────────────────────────
if page == "📖 사용 가이드":
    render_onboarding()

elif page == "📊 사용 현황":
    render_dashboard()

else:
    # ── 질의응답 ─────────────────────────────────────────────

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # ── 입력창 (헤더 바로 아래) ───────────────────────────────
    with st.form(key="query_form", clear_on_submit=True):
        col_input, col_btn = st.columns([5, 1])
        with col_input:
            prompt = st.text_input(
                "질문 입력",
                placeholder="예: 연차 유급휴가는 며칠인가요?",
                label_visibility="collapsed",
            )
        with col_btn:
            submitted = st.form_submit_button("전송 →", use_container_width=True, type="primary")

    # ── 답변 처리 ─────────────────────────────────────────────
    if submitted and prompt.strip():
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("규정을 검토하는 중..."):
            if not RAG_AVAILABLE:
                answer   = "RAG 모듈이 연결되지 않았습니다. API 키와 패키지를 확인해 주세요."
                articles = []
            else:
                try:
                    _, retriever, generator = get_rag_components()

                    if not retriever.is_ready:
                        answer   = "먼저 사이드바에서 규정 파일을 업로드하고 인덱스를 구축해 주세요."
                        articles = []
                    else:
                        t0       = time.time()
                        results  = retriever.search(prompt)
                        answer   = generator.generate(prompt, results)
                        articles = generator.extract_cited_articles(answer)
                        log_query(prompt, articles, (time.time() - t0) * 1000)

                        if results:
                            with st.expander("📄 참조된 조항 원문"):
                                for r in results:
                                    article = r.chunk.metadata.get("article", "")
                                    st.markdown(f"**{article}** (유사도: {r.score:.2f})")
                                    preview = r.chunk.text[:400]
                                    st.text(preview + ("..." if len(r.chunk.text) > 400 else ""))
                                    st.divider()

                except Exception as e:
                    answer   = f"오류가 발생했습니다: {e}"
                    articles = []

        st.session_state.messages.append({
            "role":     "assistant",
            "content":  answer,
            "articles": articles,
            "question": prompt,
        })

    # ── 대화 히스토리 (최신순) ────────────────────────────────
    for msg in reversed(st.session_state.messages):
        if msg["role"] == "user":
            st.markdown(
                f'<div class="chat-user">{msg["content"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="chat-assistant">{msg["content"]}</div>',
                unsafe_allow_html=True,
            )
            if msg.get("articles"):
                badges = " ".join(
                    f'<span class="article-badge">📌 {a}</span>'
                    for a in msg["articles"]
                )
                st.markdown(badges, unsafe_allow_html=True)
            render_feedback_widget(msg.get("question", ""), msg["content"])
