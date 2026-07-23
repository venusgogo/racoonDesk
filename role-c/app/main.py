import sys
import os
import time
import tempfile
from pathlib import Path

ROLE_C_DIR = os.path.join(os.path.dirname(__file__), "..")
REPO_ROOT   = os.path.join(os.path.dirname(__file__), "../..")
sys.path.insert(0, ROLE_C_DIR)
sys.path.insert(0, REPO_ROOT)

import streamlit as st

from ui.components.feedback_widget import render_feedback_widget, render_feedback_summary
from ui.components.metrics_dashboard import render_dashboard, log_query
from ui.components.onboarding import render_onboarding

try:
    sys.path.insert(0, os.path.join(REPO_ROOT, "role-b"))
    from rag.loader import DocumentLoader
    from rag.embedder import Embedder
    from rag.retriever import Retriever
    from rag.generator import Generator
    RAG_AVAILABLE = True
    RAG_ERROR = ""
except Exception as e:
    RAG_AVAILABLE = False
    RAG_ERROR = str(e)

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

# ── 참조 조항 원문 표시 ───────────────────────────────────────
def _render_sources(results: list) -> None:
    if not results:
        return
    with st.expander("📄 참조된 조항 원문"):
        for r in results:
            article = r.chunk.metadata.get("article", "")
            source  = r.chunk.metadata.get("source", "")
            st.markdown(
                f"**{article}** &nbsp; `유사도: {r.score:.3f}` &nbsp; `출처: {source}`"
            )
            preview = r.chunk.text[:400]
            st.text(preview + ("..." if len(r.chunk.text) > 400 else ""))
            st.divider()

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
            suffix = Path(uploaded.name).suffix
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded.read())
                tmp_path = tmp.name

            _, retriever, _ = get_rag_components()
            loader_tmp = DocumentLoader()

            if st.button("⚙️ 등록하기", type="primary", use_container_width=True):
                progress = st.progress(0, text="규정 내용 분석 중...")
                try:
                    chunks = loader_tmp.load(tmp_path)
                    progress.progress(40, text=f"{len(chunks)}개 항목 분석 완료. AI 학습 중...")
                    retriever.build_index(chunks)
                    progress.progress(80, text="저장 중...")
                    retriever.save()
                    st.cache_resource.clear()
                    progress.progress(100, text="완료!")
                    st.success(f"✅ 등록 완료: {len(chunks)}개 항목")
                except Exception as e:
                    st.error(f"등록 실패: {e}")
                finally:
                    progress.empty()

        # 인덱스 상태 표시
        try:
            _, retriever, _ = get_rag_components()
            if retriever.is_ready:
                st.info(f"📂 규정 {retriever.chunk_count}개 항목 준비 완료")
        except Exception:
            pass

        st.divider()
        st.markdown("### 검색 설정")
        top_k      = st.slider("최대 참고 조항 수", 1, 10, 5)
        threshold  = st.slider("검색 정확도", 0.0, 1.0, 0.3, step=0.05)
        use_stream = st.toggle("답변 실시간 출력", value=True)
    else:
        top_k      = 5
        threshold  = 0.3
        use_stream = False
        st.warning("AI 검색 기능을 불러올 수 없습니다.")
        if RAG_ERROR:
            st.caption(f"오류: {RAG_ERROR}")

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

    # 이번 턴 이전 메시지 스냅샷 (현재 턴 인라인 렌더링 후 중복 방지)
    previous_messages = list(st.session_state.messages)

    # ── 입력창 ───────────────────────────────────────────────
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

    # ── 현재 턴 처리 및 즉시 렌더링 ─────────────────────────
    if submitted and prompt.strip():
        # 현재 턴의 assistant 메시지가 append될 인덱스 (user 다음 자리)
        current_msg_id = len(previous_messages) + 1
        st.markdown(
            f'<div class="chat-user">{prompt}</div>',
            unsafe_allow_html=True,
        )

        answer   = ""
        articles = []
        results  = []

        if not RAG_AVAILABLE:
            answer = "AI 검색 기능을 불러올 수 없습니다. Streamlit Cloud Secrets에 GEMINI_API_KEY가 설정됐는지 확인해 주세요."
            st.markdown(f'<div class="chat-assistant">{answer}</div>', unsafe_allow_html=True)

        else:
            try:
                _, retriever, generator = get_rag_components()

                if not retriever.is_ready:
                    answer = "먼저 사이드바에서 규정 파일을 업로드하고 등록해 주세요."
                    st.markdown(f'<div class="chat-assistant">{answer}</div>', unsafe_allow_html=True)

                else:
                    t0      = time.time()
                    results = retriever.search(prompt, top_k=top_k, threshold=threshold)

                    if use_stream:
                        with st.chat_message("assistant"):
                            stream   = generator.generate(prompt, results, stream=True)
                            answer   = st.write_stream(stream)
                            articles = generator.extract_cited_articles(answer)
                            if articles:
                                badges = " ".join(
                                    f'<span class="article-badge">📌 {a}</span>'
                                    for a in articles
                                )
                                st.markdown(badges, unsafe_allow_html=True)
                            _render_sources(results)
                        render_feedback_widget(prompt, answer, msg_id=current_msg_id)
                    else:
                        with st.spinner("규정을 검토하는 중..."):
                            answer   = generator.generate(prompt, results)
                        articles = generator.extract_cited_articles(answer)
                        st.markdown(f'<div class="chat-assistant">{answer}</div>', unsafe_allow_html=True)
                        if articles:
                            badges = " ".join(
                                f'<span class="article-badge">📌 {a}</span>'
                                for a in articles
                            )
                            st.markdown(badges, unsafe_allow_html=True)
                        _render_sources(results)
                        render_feedback_widget(prompt, answer, msg_id=current_msg_id)

                    log_query(prompt, articles, (time.time() - t0) * 1000)

            except Exception as e:
                answer = f"오류가 발생했습니다: {e}"
                st.markdown(f'<div class="chat-assistant">{answer}</div>', unsafe_allow_html=True)

        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({
            "role":     "assistant",
            "content":  answer,
            "articles": articles,
            "question": prompt,
            "results":  results,
        })

    # ── 이전 대화 히스토리 (최신순) ──────────────────────────
    for i in range(len(previous_messages) - 1, -1, -1):
        msg = previous_messages[i]
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
            _render_sources(msg.get("results", []))
            render_feedback_widget(msg.get("question", ""), msg["content"], msg_id=i)
