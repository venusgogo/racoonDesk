import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st

from rag.loader import DocumentLoader
from rag.embedder import Embedder
from rag.retriever import Retriever
from rag.generator import Generator
from app.components.sidebar import render_sidebar
from app.components.chat import (
    render_chat_history,
    render_answer,
    render_streaming_answer,
)

st.set_page_config(
    page_title="인사규정 Q&A",
    page_icon="📘",
    layout="wide",
)


@st.cache_resource
def get_components():
    loader = DocumentLoader()
    embedder = Embedder()
    retriever = Retriever(embedder=embedder)
    generator = Generator()
    return loader, embedder, retriever, generator


def main():
    st.title("📘 인사규정 질의응답 시스템")
    st.caption("인사규정 문서를 업로드하고 궁금한 내용을 질문하세요.")

    loader, embedder, retriever, generator = get_components()

    # 사이드바
    is_ready, top_k, threshold, use_stream = render_sidebar(retriever, loader)

    # 세션 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 채팅 히스토리
    render_chat_history()

    # 입력
    if query := st.chat_input("인사규정에 대해 질문해 주세요.", disabled=not is_ready):
        # 사용자 메시지 저장
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        if not is_ready:
            st.warning("먼저 사이드바에서 인사규정 문서를 업로드해 주세요.")
            return

        # 검색
        with st.spinner("관련 조항 검색 중..."):
            results = retriever.search(query, top_k=top_k, threshold=threshold)

        if not results:
            with st.chat_message("assistant"):
                msg = "관련 조항을 찾지 못했습니다. 다른 표현으로 질문해 보세요."
                st.warning(msg)
            st.session_state.messages.append({"role": "assistant", "content": msg})
            return

        # 답변 생성
        if use_stream:
            stream = generator.generate(query, results, stream=True)
            answer, cited_articles = render_streaming_answer(query, stream, results, generator)
        else:
            with st.spinner("답변 생성 중..."):
                answer = generator.generate(query, results, stream=False)
            cited_articles = generator.extract_cited_articles(answer)
            render_answer(query, answer, results, cited_articles, generator)

        # 어시스턴트 메시지 저장
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
                "articles": cited_articles,
                "sources": results,
            }
        )

    # 인덱스 미준비 안내
    if not is_ready:
        st.info("👈 사이드바에서 인사규정 문서를 업로드하여 시작하세요.")


if __name__ == "__main__":
    main()
