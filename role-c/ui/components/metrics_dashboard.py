import json
import os
from datetime import datetime, timedelta
from collections import Counter
import streamlit as st

METRICS_FILE = os.path.join(os.path.dirname(__file__), "../../feedback/metrics_log.json")
FEEDBACK_FILE = os.path.join(os.path.dirname(__file__), "../../feedback/feedback_log.json")


def log_query(question: str, articles: list, response_ms: float):
    """질의 1건을 메트릭 로그에 기록합니다."""
    records = _load_metrics()
    records.append({
        "timestamp": datetime.now().isoformat(),
        "question_len": len(question),
        "articles": articles,
        "response_ms": round(response_ms),
    })
    _save_metrics(records)


def render_dashboard():
    """관리자용 사용 현황 대시보드를 렌더링합니다."""
    records = _load_metrics()
    feedback = _load_feedback()

    st.subheader("📊 사용 현황 대시보드")

    if not records:
        st.info("아직 질의 기록이 없습니다.")
        return

    # 기간 필터
    days = st.selectbox("기간", [7, 30, 90], index=0, format_func=lambda d: f"최근 {d}일")
    cutoff = datetime.now() - timedelta(days=days)
    recent = [r for r in records if datetime.fromisoformat(r["timestamp"]) > cutoff]

    # 핵심 지표
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("총 질의 수", f"{len(recent)}건")
    with col2:
        avg_ms = round(sum(r["response_ms"] for r in recent) / len(recent)) if recent else 0
        st.metric("평균 응답시간", f"{avg_ms}ms")
    with col3:
        fb_recent = [f for f in feedback if datetime.fromisoformat(f["timestamp"]) > cutoff]
        helpful = sum(1 for f in fb_recent if f.get("helpful"))
        rate = round(helpful / len(fb_recent) * 100) if fb_recent else 0
        st.metric("긍정 피드백", f"{rate}%")
    with col4:
        daily_avg = round(len(recent) / days, 1)
        st.metric("일평균 질의", f"{daily_avg}건")

    st.divider()

    # 자주 참조된 조항 Top 5
    all_articles = []
    for r in recent:
        all_articles.extend(r.get("articles", []))

    if all_articles:
        st.caption("📌 자주 참조된 조항 Top 5")
        top_articles = Counter(all_articles).most_common(5)
        for article, count in top_articles:
            bar_width = int(count / top_articles[0][1] * 100)
            st.markdown(
                f"`{article}` — {count}회  "
                f"<div style='background:#6B4F3A;height:6px;width:{bar_width}%;border-radius:3px'></div>",
                unsafe_allow_html=True,
            )

    # 부정 피드백 사유
    negative = [f for f in fb_recent if not f.get("helpful") and f.get("reason")]
    if negative:
        st.divider()
        st.caption("⚠️ 최근 개선 의견")
        for fb in negative[-5:]:
            ts = fb["timestamp"][:10]
            st.markdown(f"- `{ts}` {fb['reason']}")


def _load_metrics() -> list:
    if not os.path.exists(METRICS_FILE):
        return []
    with open(METRICS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_metrics(records: list):
    os.makedirs(os.path.dirname(METRICS_FILE), exist_ok=True)
    with open(METRICS_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def _load_feedback() -> list:
    if not os.path.exists(FEEDBACK_FILE):
        return []
    with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
