from typing import Optional
import anthropic

from config.settings import ANTHROPIC_API_KEY, CLAUDE_MODEL, MAX_TOKENS
from rag.retriever import SearchResult


SYSTEM_PROMPT = """당신은 회사 인사규정 전문 어시스턴트입니다.
주어진 인사규정 조항들을 바탕으로 질문에 정확하고 친절하게 답변합니다.

답변 규칙:
1. 반드시 제공된 조항 내용만을 근거로 답변하세요.
2. 답변 말미에 근거 조항을 "[근거: 제X조 (조항명)]" 형식으로 명시하세요.
3. 여러 조항이 근거인 경우 모두 나열하세요.
4. 제공된 조항에서 답을 찾을 수 없으면 "제공된 규정에서 해당 내용을 찾을 수 없습니다."라고 답하세요.
5. 불확실한 내용은 추측하지 말고 규정 내용만 전달하세요."""


def _build_context(results: list[SearchResult]) -> str:
    if not results:
        return "관련 조항을 찾지 못했습니다."

    lines = ["[관련 인사규정 조항]"]
    for r in results:
        article = r.chunk.metadata.get("article", "미상")
        lines.append(f"\n--- {article} (유사도: {r.score:.2f}) ---")
        lines.append(r.chunk.text.strip())

    return "\n".join(lines)


class Generator:
    def __init__(
        self,
        model: str = CLAUDE_MODEL,
        max_tokens: int = MAX_TOKENS,
        api_key: Optional[str] = None,
    ):
        self.model = model
        self.max_tokens = max_tokens
        key = api_key or ANTHROPIC_API_KEY
        if not key:
            raise EnvironmentError(
                "ANTHROPIC_API_KEY가 설정되지 않았습니다. "
                "Streamlit Cloud → App settings → Secrets에 ANTHROPIC_API_KEY를 추가하세요."
            )
        self.client = anthropic.Anthropic(api_key=key)

    def generate(
        self,
        query: str,
        search_results: list[SearchResult],
        stream: bool = False,
    ) -> str:
        context = _build_context(search_results)
        user_message = f"{context}\n\n[질문]\n{query}"

        if stream:
            return self._stream(user_message)
        return self._invoke(user_message)

    def _invoke(self, user_message: str) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        return response.content[0].text

    def _stream(self, user_message: str):
        """스트리밍 제너레이터를 반환합니다 (Streamlit st.write_stream 호환)."""
        with self.client.messages.stream(
            model=self.model,
            max_tokens=self.max_tokens,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        ) as stream:
            for text in stream.text_stream:
                yield text

    def extract_cited_articles(self, answer: str) -> list[str]:
        """답변 텍스트에서 '[근거: ...]' 패턴의 조항 번호를 추출합니다."""
        import re
        pattern = re.compile(r"\[근거:\s*([^\]]+)\]")
        matches = pattern.findall(answer)
        articles: list[str] = []
        for match in matches:
            # 쉼표로 구분된 복수 조항 분리
            parts = [p.strip() for p in match.split(",")]
            articles.extend(parts)
        return articles
