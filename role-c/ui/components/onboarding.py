import streamlit as st


STEPS = [
    ("📁", "규정 파일 올리기",  "왼쪽 메뉴에서 인사관리 규정 파일을 올려주세요."),
    ("⚙️", "규정 등록하기",    "'등록하기' 버튼을 누르면 AI가 규정 내용을 학습합니다. 처음 한 번만 하면 됩니다."),
    ("💬", "질문 입력",        "입력창에 궁금한 것을 자유롭게 질문하세요.\n예: '육아휴직은 며칠까지 쓸 수 있나요?'"),
    ("📌", "관련 조항 확인",   "답변과 함께 관련 조항 번호가 표시됩니다. '참조된 조항 원문' 버튼으로 원문을 확인하세요."),
    ("👍", "피드백 남기기",    "답변 하단의 👍/👎 버튼으로 의견을 남겨주세요. 서비스 개선에 활용됩니다."),
]

FAQ = [
    ("어떤 파일 형식을 올릴 수 있나요?", "PDF, Word(.docx), Markdown(.md), 텍스트(.txt) 파일을 지원합니다. 조항이 '제N조' 형식으로 구분되어 있을수록 답변 정확도가 높아집니다."),
    ("규정에 없는 내용을 물어보면 어떻게 되나요?", "AI가 임의로 답변을 만들지 않고, '해당 내용은 규정에서 찾을 수 없습니다'라고 안내합니다."),
    ("규정 파일이 바뀌면 어떻게 해야 하나요?", "사이드바에서 새 파일을 올리고 '등록하기' 버튼을 다시 누르면 됩니다."),
    ("답변이 틀린 것 같아요.", "👎 버튼으로 의견을 남겨주세요. 인사팀에 직접 문의하실 때는 표시된 관련 조항을 참고하시면 됩니다."),
]


def render_onboarding():
    """처음 사용자를 위한 온보딩 가이드 페이지를 렌더링합니다."""
    st.markdown("## 🦝 RACOON 사용 가이드")
    st.caption("인사관리 규정 AI 질의응답 시스템 시작하기")
    st.divider()

    st.markdown("### 사용 방법")
    for i, (icon, title, desc) in enumerate(STEPS, 1):
        cols = st.columns([0.08, 0.92])
        with cols[0]:
            st.markdown(
                f"<div style='background:#6B4F3A;color:#FFF;width:28px;height:28px;"
                f"border-radius:50%;display:flex;align-items:center;justify-content:center;"
                f"font-size:0.8rem;font-weight:700;margin-top:4px'>{i}</div>",
                unsafe_allow_html=True,
            )
        with cols[1]:
            st.markdown(f"**{icon} {title}**")
            st.caption(desc)
        if i < len(STEPS):
            st.markdown("<div style='border-left:2px dashed #DDD8D3;height:16px;margin-left:13px'></div>", unsafe_allow_html=True)

    st.divider()
    st.markdown("### 자주 묻는 질문")
    for q, a in FAQ:
        with st.expander(q):
            st.write(a)

    st.divider()
    st.info("문의: 인사팀 내선 ○○○○ | 시스템 오류: IT팀 내선 ○○○○")
