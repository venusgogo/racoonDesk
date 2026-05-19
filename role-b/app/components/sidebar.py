import streamlit as st
import tempfile
from pathlib import Path


def render_sidebar(retriever, loader) -> bool:
    """사이드바: 문서 업로드 및 인덱싱. 인덱스가 준비되면 True 반환."""
    with st.sidebar:
        st.header("📂 인사규정 문서 업로드")

        uploaded_file = st.file_uploader(
            "PDF, TXT, DOCX 파일을 업로드하세요",
            type=["pdf", "txt", "docx", "md"],
            help="인사규정 문서를 업로드하면 자동으로 인덱싱됩니다.",
        )

        if uploaded_file:
            if st.button("🔄 문서 인덱싱", use_container_width=True):
                _index_document(uploaded_file, retriever, loader)

        st.divider()

        # 저장된 인덱스 로드 시도
        if not retriever.is_ready:
            with st.spinner("저장된 인덱스 로드 중..."):
                loaded = retriever.load()
            if loaded:
                st.success(f"✅ 인덱스 로드 완료 ({retriever.chunk_count}개 청크)")
            else:
                st.info("ℹ️ 문서를 업로드하여 인덱스를 생성해 주세요.")
        else:
            st.success(f"✅ 인덱스 준비 완료 ({retriever.chunk_count}개 청크)")

        st.divider()
        st.caption("**설정**")

        top_k = st.slider("검색할 조항 수 (Top-K)", 1, 10, 5)
        threshold = st.slider("유사도 임계값", 0.0, 1.0, 0.3, step=0.05)
        stream = st.toggle("스트리밍 답변", value=True)

        return retriever.is_ready, top_k, threshold, stream


def _index_document(uploaded_file, retriever, loader) -> None:
    suffix = Path(uploaded_file.name).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    progress = st.progress(0, text="문서 청킹 중...")
    try:
        chunks = loader.load(tmp_path)
        progress.progress(40, text=f"{len(chunks)}개 청크 생성. 임베딩 중...")

        retriever.build_index(chunks)
        progress.progress(80, text="인덱스 저장 중...")

        retriever.save()
        progress.progress(100, text="완료!")
        st.success(f"✅ 인덱싱 완료: {len(chunks)}개 청크")
        st.rerun()
    except Exception as e:
        st.error(f"인덱싱 실패: {e}")
    finally:
        progress.empty()
