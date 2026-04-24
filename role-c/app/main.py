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

# Role B RAG 엔진 연결
try:
    from role_b.rag.loader import load_markdown, chunk_by_article
    from role_b.rag.embedder import build_vectorstore, load_vectorstore
    from role_b.rag.retriever import retrieve
    from role_b.rag.generator import generate_answer
    from role_b.config.settings import VECTORSTORE_DIR
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False

# ── 페이지 설정 ──────────────────────────────────────────────
st.set_page_config(
    page_title="RACOON — HR 규정 도우미",
    page_icon="🦝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS 로드 ─────────────────────────────────────────────────
css_path = os.path.join(os.path.dirname(__file__), "../ui/styles/racoon_theme.css")
if os.path.exists(css_path):
    with open(css_path, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── 헤더 ─────────────────────────────────────────────────────
st.markdown("""
<div class="racoon-header">
  <div>
    <h1>🦝 RACOON</h1>
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
        uploaded = st.file_uploader("Markdown 파일 업로드", type=["md", "txt"])
        if uploaded:
            content = uploaded.read().decode("utf-8")
            chunks = chunk_by_article(content)
            st.info(f"조항 {len(chunks)}개 감지됨")
            if st.button("⚙️ 인덱스 구축", type="primary", use_container_width=True):
                with st.spinner("학습 중..."):
                    build_vectorstore(chunks)
                st.success("완료!")
    else:
        st.warning("Role B RAG 모듈을 찾을 수 없습니다.\nrole-b 패키지를 먼저 설치하세요.")

    st.divider()
    st.markdown("### 피드백 현황")
    render_feedback_summary()
    st.divider()
    st.caption("RACOON v1.0 · Role C UX")

# ── 페이지 라우팅 ──────────────────────────────────────────────
if page == "📖 사용 가이드":
    render_onboarding()

elif page == "📊 사용 현황":
    render_dashboard()

else:
    # ── 질의응답 ─────────────────────────────────────────────
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 대화 히스토리 출력
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-user">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-assistant">{msg["content"]}</div>', unsafe_allow_html=True)
            if msg.get("articles"):
                badges = " ".join(
                    f'<span class="article-badge">📌 {a}</span>'
                    for a in msg["articles"]
                )
                st.markdown(badges, unsafe_allow_html=True)
            render_feedback_widget(msg.get("question", ""), msg["content"])

    # 입력창
    if prompt := st.chat_input("인사관리 규정에 대해 질문하세요..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.markdown(f'<div class="chat-user">{prompt}</div>', unsafe_allow_html=True)

        with st.spinner("규정을 검토하는 중..."):
            if not RAG_AVAILABLE:
                answer = "RAG 모듈이 연결되지 않았습니다. role-b 패키지를 설치해 주세요."
                articles = []
            else:
                try:
                    t0 = time.time()
                    index, chunks = load_vectorstore(VECTORSTORE_DIR)
                    retrieved = retrieve(prompt, index, chunks)
                    result = generate_answer(prompt, retrieved)
                    elapsed_ms = (time.time() - t0) * 1000

                    answer = result["answer"]
                    articles = result["source_articles"]
                    log_query(prompt, articles, elapsed_ms)

                    with st.expander("📄 참조된 조항 원문"):
                        for chunk in result["retrieved_chunks"]:
                            st.markdown(f"**{chunk['article']}**")
                            preview = chunk["content"][:400]
                            st.text(preview + ("..." if len(chunk["content"]) > 400 else ""))
                            st.divider()

                except FileNotFoundError:
                    answer = "먼저 사이드바에서 규정 파일을 업로드하고 인덱스를 구축해 주세요."
                    articles = []
                except Exception as e:
                    answer = f"오류가 발생했습니다: {e}"
                    articles = []

        st.markdown(f'<div class="chat-assistant">{answer}</div>', unsafe_allow_html=True)
        if articles:
            badges = " ".join(f'<span class="article-badge">📌 {a}</span>' for a in articles)
            st.markdown(badges, unsafe_allow_html=True)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "articles": articles,
            "question": prompt,
        })
        render_feedback_widget(prompt, answer)
