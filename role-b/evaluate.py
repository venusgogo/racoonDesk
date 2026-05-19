"""
Role A 테스트셋으로 RAG 시스템 정확도를 검증합니다.

사용법:
    python evaluate.py --testset data/testset.json --output data/eval_result.json

테스트셋 형식 (Role A 제공):
[
  {
    "question": "연차 휴가는 며칠인가요?",
    "expected_articles": ["제20조", "제21조"],
    "expected_keywords": ["연차", "15일"]
  },
  ...
]
"""

import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from rag.loader import DocumentLoader
from rag.embedder import Embedder
from rag.retriever import Retriever
from rag.generator import Generator


def article_recall(expected: list[str], retrieved: list[str]) -> float:
    """예상 조항 중 검색된 비율."""
    if not expected:
        return 1.0
    hits = sum(1 for e in expected if any(e in r for r in retrieved))
    return hits / len(expected)


def keyword_hit(expected_keywords: list[str], answer: str) -> float:
    """예상 키워드 중 답변에 포함된 비율."""
    if not expected_keywords:
        return 1.0
    hits = sum(1 for kw in expected_keywords if kw in answer)
    return hits / len(expected_keywords)


def evaluate(testset_path: str, output_path: str, top_k: int = 5) -> dict:
    retriever = Retriever()
    if not retriever.load():
        raise RuntimeError("저장된 인덱스가 없습니다. 먼저 문서를 인덱싱하세요.")

    generator = Generator()

    with open(testset_path, encoding="utf-8") as f:
        testset = json.load(f)

    results = []
    total_recall = 0.0
    total_kw_hit = 0.0

    for i, item in enumerate(testset, 1):
        question = item["question"]
        expected_articles = item.get("expected_articles", [])
        expected_keywords = item.get("expected_keywords", [])

        search_results = retriever.search(question, top_k=top_k)
        retrieved_articles = retriever.get_unique_articles(search_results)

        answer = generator.generate(question, search_results, stream=False)
        cited_articles = generator.extract_cited_articles(answer)

        recall = article_recall(expected_articles, retrieved_articles)
        kw = keyword_hit(expected_keywords, answer)

        total_recall += recall
        total_kw_hit += kw

        result = {
            "id": i,
            "question": question,
            "expected_articles": expected_articles,
            "retrieved_articles": retrieved_articles,
            "cited_articles": cited_articles,
            "article_recall": round(recall, 3),
            "keyword_hit_rate": round(kw, 3),
            "answer": answer,
        }
        results.append(result)
        print(f"[{i}/{len(testset)}] recall={recall:.2f} kw_hit={kw:.2f} | {question[:40]}")

    n = len(testset)
    summary = {
        "total": n,
        "avg_article_recall": round(total_recall / n, 3),
        "avg_keyword_hit_rate": round(total_kw_hit / n, 3),
        "results": results,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"\n=== 평가 완료 ===")
    print(f"조항 Recall:   {summary['avg_article_recall']:.3f}")
    print(f"키워드 Hit율:  {summary['avg_keyword_hit_rate']:.3f}")
    print(f"결과 저장: {output_path}")

    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--testset", default="data/testset.json")
    parser.add_argument("--output", default="data/eval_result.json")
    parser.add_argument("--top_k", type=int, default=5)
    args = parser.parse_args()

    evaluate(args.testset, args.output, top_k=args.top_k)
