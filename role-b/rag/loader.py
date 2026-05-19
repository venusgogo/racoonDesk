import re
import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader

from config.settings import CHUNK_SIZE, CHUNK_OVERLAP


@dataclass
class Chunk:
    text: str
    metadata: dict = field(default_factory=dict)
    chunk_id: str = ""


# 인사규정 조항 패턴: "제1조", "제12조의2", "제3장" 등
ARTICLE_PATTERN = re.compile(
    r"(제\s*\d+\s*조(?:의\s*\d+)?|제\s*\d+\s*장|제\s*\d+\s*절)\s*[（(]?([^)\n）]{0,40})[）)]?"
)


def _extract_article_number(text: str) -> Optional[str]:
    """텍스트 앞부분에서 조항 번호를 추출합니다."""
    match = ARTICLE_PATTERN.search(text[:200])
    if match:
        article = match.group(1).replace(" ", "")
        title = match.group(2).strip()
        return f"{article} {title}".strip() if title else article
    return None


def _split_by_article(text: str) -> list[dict]:
    """조항 단위로 텍스트를 분리합니다."""
    segments = []
    positions = [(m.start(), m.group()) for m in ARTICLE_PATTERN.finditer(text)]

    if not positions:
        return [{"text": text, "article": None}]

    for i, (start, header) in enumerate(positions):
        end = positions[i + 1][0] if i + 1 < len(positions) else len(text)
        segment_text = text[start:end].strip()
        article_num = header.replace(" ", "")
        segments.append({"text": segment_text, "article": article_num})

    # 첫 조항 이전 서문이 있으면 앞에 추가
    if positions[0][0] > 0:
        preamble = text[: positions[0][0]].strip()
        if preamble:
            segments.insert(0, {"text": preamble, "article": "서문"})

    return segments


class DocumentLoader:
    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "。", ".", " ", ""],
        )

    def load(self, file_path: str) -> list[Chunk]:
        path = Path(file_path)
        ext = path.suffix.lower()

        if ext == ".pdf":
            raw_docs = PyPDFLoader(file_path).load()
        elif ext in (".txt", ".md"):
            raw_docs = TextLoader(file_path, encoding="utf-8").load()
        elif ext in (".docx", ".doc"):
            raw_docs = Docx2txtLoader(file_path).load()
        else:
            raise ValueError(f"지원하지 않는 파일 형식: {ext}")

        full_text = "\n\n".join(doc.page_content for doc in raw_docs)
        return self._chunk(full_text, source=path.name)

    def load_from_text(self, text: str, source: str = "manual") -> list[Chunk]:
        return self._chunk(text, source=source)

    def _chunk(self, text: str, source: str) -> list[Chunk]:
        chunks: list[Chunk] = []
        article_segments = _split_by_article(text)

        for seg in article_segments:
            seg_text = seg["text"]
            article = seg["article"]

            # 조항이 chunk_size보다 짧으면 그대로 사용
            if len(seg_text) <= self.chunk_size:
                chunk_id = f"{source}::{article or 'unknown'}::0"
                chunks.append(
                    Chunk(
                        text=seg_text,
                        metadata={"source": source, "article": article, "chunk_index": 0},
                        chunk_id=chunk_id,
                    )
                )
            else:
                # 긴 조항은 RecursiveCharacterTextSplitter로 재분할
                sub_texts = self.splitter.split_text(seg_text)
                for i, sub in enumerate(sub_texts):
                    chunk_id = f"{source}::{article or 'unknown'}::{i}"
                    chunks.append(
                        Chunk(
                            text=sub,
                            metadata={"source": source, "article": article, "chunk_index": i},
                            chunk_id=chunk_id,
                        )
                    )

        return chunks

    @staticmethod
    def save_chunks(chunks: list[Chunk], output_path: str) -> None:
        data = [
            {"chunk_id": c.chunk_id, "text": c.text, "metadata": c.metadata}
            for c in chunks
        ]
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def load_chunks(input_path: str) -> list[Chunk]:
        with open(input_path, encoding="utf-8") as f:
            data = json.load(f)
        return [Chunk(text=d["text"], metadata=d["metadata"], chunk_id=d["chunk_id"]) for d in data]
