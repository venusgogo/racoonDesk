import streamlit as st
from rag.retriever import SearchResult


def render_chat_history() -> None:
    for msg in st.session_state.get("messages", []):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and msg.get("articles"):
                _render_citations(msg["articles"])
            if msg["role"] == "assistant" and msg.get("sources"):
                _render_sources(msg["sources"])


def render_answer(
    query: str,
    answer: str,
    search_results: list[SearchResult],
    cited_articles: list[str],
    generator,
) -> None:
    with st.chat_message("assistant"):
        st.markdown(answer)
        if cited_articles:
            _render_citations(cited_articles)
        if search_results:
            _render_sources(search_results)


def render_streaming_answer(
    query: str,
    stream,
    search_results: list[SearchResult],
    generator,
) -> str:
    """스트리밍 답변을 렌더링하고 전체 텍스트를 반환합니다."""
    with st.chat_message("assistant"):
        answer = st.write_stream(stream)
        cited_articles = generator.extract_cited_articles(answer)
        if cited_articles:
            _render_citations(cited_articles)
        if search_results:
            _render_sources(search_results)
    return answer, cited_articles


def _render_citations(articles: list[str]) -> None:
    if not articles:
        return
    badge_html = " ".join(
        f'<span style="background:#e8f0fe;color:#1a73e8;padding:2px 8px;border-radius:12px;font-size:0.85em;margin:2px">{a}</span>'
        for a in articles
    )
    st.markdown(f"**근거 조항:** {badge_html}", unsafe_allow_html=True)


def _render_sources(search_results: list[SearchResult]) -> None:
    with st.expander("📋 참고 조항 상세보기", expanded=False):
        for r in search_results:
            article = r.chunk.metadata.get("article", "미상")
            source = r.chunk.metadata.get("source", "")
            st.markdown(
                f"**{article}** &nbsp; `유사도: {r.score:.3f}` &nbsp; `출처: {source}`"
            )
            st.text(r.chunk.text[:400] + ("..." if len(r.chunk.text) > 400 else ""))
            st.divider()
