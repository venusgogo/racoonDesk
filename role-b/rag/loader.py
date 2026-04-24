import re
from pathlib import Path
from typing import List, Dict


def load_markdown(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def chunk_by_article(text: str) -> List[Dict]:
    """
    인사관리 규정을 '제N조' 단위로 청킹합니다.
    각 청크에 조항 번호 메타데이터를 포함합니다.
    """
    # 제N조 패턴으로 분할
    pattern = r"(제\d+조[^\n]*\n)"
    parts = re.split(pattern, text)

    chunks = []
    current_article = None
    current_content = []

    for part in parts:
        article_match = re.match(r"(제\d+조[^\n]*)", part.strip())
        if article_match:
            if current_article and current_content:
                chunks.append({
                    "article": current_article,
                    "content": current_article + "\n" + "".join(current_content).strip(),
                })
            current_article = article_match.group(1)
            current_content = []
        else:
            current_content.append(part)

    if current_article and current_content:
        chunks.append({
            "article": current_article,
            "content": current_article + "\n" + "".join(current_content).strip(),
        })

    return chunks


def chunk_fixed_size(text: str, chunk_size: int = 500, overlap: int = 50) -> List[Dict]:
    """조항 구분이 어려울 때 사용하는 고정 크기 청킹."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk_text = text[start:end]

        # 조항 번호 추출 시도
        article_match = re.search(r"제\d+조", chunk_text)
        article = article_match.group(0) if article_match else "N/A"

        chunks.append({"article": article, "content": chunk_text})
        start += chunk_size - overlap

    return chunks
