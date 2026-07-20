# Role B — RAG 시스템 및 파이프라인 개발자

담당 AI: **Claude**

## 임무

인사규정 데이터를 기반으로 답변을 생성하는 RAG 시스템 엔진을 구축합니다.

## 작업 목록

- [ ] Streamlit 기반 파일 업로드 및 질의응답 앱 구성
- [ ] 문서 청킹 및 임베딩 파이프라인 구현
- [ ] 벡터 검색 기반 유사 조항 검색 로직 개발
- [ ] 근거 조항 번호 출력 로직 고도화
- [ ] Role A 테스트셋으로 정확도 검증

## 디렉토리 구조

```
role-b/
├── app/
│   ├── main.py          ← Streamlit 메인 앱
│   └── components/      ← UI 컴포넌트
├── rag/
│   ├── __init__.py
│   ├── loader.py        ← 문서 로딩 및 청킹
│   ├── embedder.py      ← 임베딩 생성
│   ├── retriever.py     ← 벡터 검색
│   └── generator.py     ← 답변 생성 (LLM 호출)
└── config/
    └── settings.py      ← 모델, 경로 등 설정
```

## 기술 스택

| 구성요소 | 선택 |
|---------|------|
| UI 프레임워크 | Streamlit |
| 임베딩 모델 | OpenAI `text-embedding-3-small` 또는 로컬 모델 |
| 벡터 DB | FAISS (로컬) |
| LLM | Gemini API |
| 문서 처리 | LangChain / llamaindex |

## 설치 및 실행

```bash
cd role-b
pip install -r requirements.txt
streamlit run app/main.py
```

## 커밋 예시

```bash
git checkout role-b/rag-pipeline
git add role-b/rag/retriever.py
git commit -m "[role-b] feat: FAISS 벡터 검색 로직 구현"
git push origin role-b/rag-pipeline
```
