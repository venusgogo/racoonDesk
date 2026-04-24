import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st

from rag.loader import load_markdown, chunk_by_article
from rag.embedder import build_vectorstore, load_vectorstore
from rag.retriever import retrieve
from rag.generator import generate_answer
from config.settings import VECTORSTORE_DIR

st.set_page_config(
    page_title="RACOON — HR 규정 AI 어시스턴트",
    page_icon="🦝",
    layout="wide",
)

st.title("🦝 RACOON")
st.caption("인사관리 규정 AI 질의응답 시스템")

# 사이드바: 파일 업로드 및 인덱스 구축
with st.sidebar:
    st.header("규정 파일 관리")
    uploaded_file = st.file_uploader(
        "인사관리 규정 파일 업로드 (Markdown)",
        type=["md", "txt"],
    )

    if uploaded_file:
        content = uploaded_file.read().decode("utf-8")
        chunks = chunk_by_article(content)
        st.info(f"총 {len(chunks)}개 조항 청크 생성됨")

        if st.button("벡터 인덱스 구축", type="primary"):
            with st.spinner("임베딩 생성 중..."):
                build_vectorstore(chunks)
            st.success("인덱스 구축 완료!")

    st.divider()
    st.caption("Role B — RAG Pipeline by Claude")

# 메인: 질의응답
st.header("규정 질의응답")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("인사관리 규정에 대해 질문하세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            index, chunks = load_vectorstore(VECTORSTORE_DIR)
            retrieved = retrieve(prompt, index, chunks)
            result = generate_answer(prompt, retrieved)

            st.markdown(result["answer"])

            with st.expander("📄 참조된 조항 원문 보기"):
                for chunk in result["retrieved_chunks"]:
                    st.markdown(f"**{chunk['article']}**")
                    st.text(chunk["content"][:300] + "..." if len(chunk["content"]) > 300 else chunk["content"])
                    st.divider()

            st.session_state.messages.append({"role": "assistant", "content": result["answer"]})

        except FileNotFoundError:
            msg = "먼저 사이드바에서 규정 파일을 업로드하고 인덱스를 구축해주세요."
            st.warning(msg)
            st.session_state.messages.append({"role": "assistant", "content": msg})
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
