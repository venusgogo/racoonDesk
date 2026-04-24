import os
from typing import List, Dict
import anthropic

from config.settings import LLM_MODEL, LLM_MAX_TOKENS, LLM_TEMPERATURE


client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

SYSTEM_PROMPT = """당신은 회사 인사관리 규정 전문 AI 어시스턴트입니다.

규칙:
1. 반드시 제공된 규정 문서의 내용만을 근거로 답변하세요.
2. 답변 마지막에 반드시 근거 조항을 명시하세요.
3. 규정에 없는 내용은 추측하거나 생성하지 마세요.
4. 규정에 없는 질문은 "해당 내용은 인사관리 규정에 명시되어 있지 않습니다. 인사팀에 문의하시기 바랍니다."라고 답하세요.

답변 형식:
[답변 내용]

📌 근거: [조항 번호]"""


def generate_answer(query: str, retrieved_chunks: List[Dict]) -> Dict:
    """검색된 조항을 바탕으로 답변을 생성합니다."""
    context = "\n\n---\n\n".join([chunk["content"] for chunk in retrieved_chunks])
    articles = [chunk["article"] for chunk in retrieved_chunks if chunk.get("article")]

    user_message = f"""다음은 인사관리 규정의 관련 조항입니다:

{context}

질문: {query}

위 규정을 바탕으로 정확하게 답변해주세요."""

    response = client.messages.create(
        model=LLM_MODEL,
        max_tokens=LLM_MAX_TOKENS,
        temperature=LLM_TEMPERATURE,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    answer_text = response.content[0].text

    return {
        "answer": answer_text,
        "source_articles": articles,
        "retrieved_chunks": retrieved_chunks,
    }
