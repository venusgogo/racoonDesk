import re
from typing import Optional
import google.generativeai as genai

from config.settings import GEMINI_API_KEY
GEMINI_MODEL = "gemini-3.5-flash"
from rag.retriever import SearchResult


SYSTEM_PROMPT = """당신은 회사 인사규정 전문 어시스턴트입니다.
주어진 인사규정 조항들을 바탕으로 질문에 정확하고 친절하게 답변합니다.

답변 규칙:
1. 반드시 제공된 조항 내용만을 근거로 답변하세요.
2. 답변 말미에 근거 조항을 "[근거: 제X조 (조항명)]" 형식으로 명시하세요.
3. 여러 조항이 근거인 경우 모두 나열하세요.
4. 제공된 조항에서 답을 찾을 수 없으면 "제공된 규정에서 해당 내용을 찾을 수 없습니다."라고 답하세요.
5. 불확실한 내용은 추측하지 말고 규정 내용만 전달하세요."""


def _api_error_message(e: Exception) -> str:
    name = type(e).__name__
    if "ResourceExhausted" in name:
        return "⚠️ AI 답변 생성 한도를 초과했습니다. 잠시 후 다시 시도해 주세요. (무료 티어: 분당 10건)"
    if "NotFound" in name:
        return "⚠️ AI 모델을 찾을 수 없습니다. 관리자에게 문의하세요."
    if "InvalidArgument" in name or "PermissionDenied" in name:
        return "⚠️ API 키가 유효하지 않습니다. Streamlit Cloud Secrets의 GEMINI_API_KEY를 확인하세요."
    return f"⚠️ 오류가 발생했습니다: {name}"


def _build_context(results: list[SearchResult]) -> str:
    if not results:
        return "관련 조항을 찾지 못했습니다."

    lines = ["[관련 인사규정 조항]"]
    for r in results:
        article = r.chunk.metadata.get("article", "미상")
        lines.append(f"\n--- {article} (유사도: {r.score:.2f}) ---")
        lines.append(r.chunk.text.strip())

    return "\n".join(lines)


def _build_retrieval_answer(query: str, results: list[SearchResult]) -> str:
    """API 키 없는 검색 전용 모드: 관련 조항을 보기 좋게 포맷하여 반환합니다."""
    lines = [f"**📌 '{query}'에 관련된 인사규정 조항입니다.**\n"]
    lines.append("> ℹ️ GEMINI_API_KEY가 없어 검색 전용 모드로 동작합니다.\n")

    for i, r in enumerate(results, start=1):
        article = r.chunk.metadata.get("article", "미상")
        lines.append(f"---\n**{i}. {article}** (유사도: {r.score:.2f})\n")
        lines.append(r.chunk.text.strip())
        lines.append("")

    return "\n".join(lines)


class Generator:
    def __init__(self, model: str = GEMINI_MODEL, api_key: Optional[str] = None):
        self.model_name = model
        key = api_key or GEMINI_API_KEY
        self.use_llm = bool(key)

        if self.use_llm:
            genai.configure(api_key=key)
            self._model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=SYSTEM_PROMPT,
            )
        else:
            self._model = None

    def generate(self, query: str, search_results: list[SearchResult], stream: bool = False):
        if not self.use_llm:
            answer = _build_retrieval_answer(query, search_results)
            if stream:
                def _fake_stream():
                    for char in answer:
                        yield char
                return _fake_stream()
            return answer

        user_message = f"{_build_context(search_results)}\n\n[질문]\n{query}"

        if stream:
            return self._stream(user_message)
        return self._invoke(user_message)

    def _invoke(self, user_message: str) -> str:
        try:
            response = self._model.generate_content(user_message)
            return response.text
        except Exception as e:
            return _api_error_message(e)

    def _stream(self, user_message: str):
        """스트리밍 제너레이터 (Streamlit st.write_stream 호환)."""
        try:
            response = self._model.generate_content(user_message, stream=True)
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            yield _api_error_message(e)

    def extract_cited_articles(self, answer: str) -> list[str]:
        """답변 텍스트에서 '[근거: ...]' 패턴의 조항 번호를 추출합니다."""
        pattern = re.compile(r"\[근거:\s*([^\]]+)\]")
        articles: list[str] = []
        for match in pattern.findall(answer):
            articles.extend(p.strip() for p in match.split(","))
        return articles
