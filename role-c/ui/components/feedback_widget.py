import json
import os
from datetime import datetime
import streamlit as st

FEEDBACK_FILE = os.path.join(os.path.dirname(__file__), "../../feedback/feedback_log.json")


def _load_feedback() -> list:
    if not os.path.exists(FEEDBACK_FILE):
        return []
    with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_feedback(records: list):
    os.makedirs(os.path.dirname(FEEDBACK_FILE), exist_ok=True)
    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def render_feedback_widget(question: str, answer: str):
    """답변 하단에 인라인 피드백 위젯을 렌더링합니다."""
    key = f"fb_{hash(question + answer) % 100000}"

    if st.session_state.get(f"{key}_submitted"):
        st.caption("✅ 피드백 감사합니다!")
        return

    with st.container():
        st.caption("이 답변이 도움이 됐나요?")
        cols = st.columns([1, 1, 4])

        with cols[0]:
            if st.button("👍 도움됨", key=f"{key}_up"):
                _record(question, answer, rating=5, helpful=True)
                st.session_state[f"{key}_submitted"] = True
                st.rerun()

        with cols[1]:
            if st.button("👎 아님", key=f"{key}_down"):
                st.session_state[f"{key}_show_detail"] = True

    if st.session_state.get(f"{key}_show_detail"):
        with st.form(key=f"{key}_form"):
            reason = st.text_area(
                "어떤 점이 아쉬웠나요?",
                placeholder="예: 답변이 틀렸어요 / 조항이 잘못됐어요 / 더 자세했으면 좋겠어요",
                max_chars=300,
            )
            submitted = st.form_submit_button("제출")
            if submitted:
                _record(question, answer, rating=1, helpful=False, reason=reason)
                st.session_state[f"{key}_submitted"] = True
                st.session_state[f"{key}_show_detail"] = False
                st.rerun()


def render_feedback_summary():
    """사이드바 등에서 전체 피드백 요약을 보여줍니다."""
    records = _load_feedback()
    if not records:
        st.caption("아직 피드백이 없습니다.")
        return

    total = len(records)
    helpful = sum(1 for r in records if r.get("helpful"))
    rate = round(helpful / total * 100) if total else 0

    st.metric("총 피드백", f"{total}건")
    st.metric("긍정 비율", f"{rate}%")


def _record(question: str, answer: str, rating: int, helpful: bool, reason: str = ""):
    records = _load_feedback()
    records.append({
        "timestamp": datetime.now().isoformat(),
        "question": question[:200],
        "answer_preview": answer[:200],
        "rating": rating,
        "helpful": helpful,
        "reason": reason,
    })
    _save_feedback(records)
