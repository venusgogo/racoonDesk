# RACOON — HR Policy RAG System

> 인사관리 규정 기반 AI 질의응답 시스템

## 프로젝트 개요

직원들이 인사관리 규정을 쉽고 빠르게 조회할 수 있도록, RAG(Retrieval-Augmented Generation) 기술을 활용한 AI 챗봇 서비스입니다.

---

## 팀 구성 및 브랜치 전략

| 역할 | 담당 AI | 브랜치 | 주요 임무 |
|------|---------|--------|-----------|
| **A — 데이터 정제 & 도메인 전문가** | Gemini | `role-a/data-refinement` | 규정 데이터 정제, 테스트셋 구축, 답변 가이드라인 |
| **B — RAG 시스템 & 파이프라인 개발자** | Claude | `role-b/rag-pipeline` | Streamlit 앱, RAG 로직, 조항 번호 출력 |
| **C — 서비스 기획 & UX 관리자** | 통합관리 | `role-c/ux-service` | UI 설계, 사용자 테스트, 성과 리포트 |

---

## 브랜치 구조

```
main
├── role-a/data-refinement     ← Gemini (데이터 담당)
├── role-b/rag-pipeline        ← Claude (엔진 담당)
└── role-c/ux-service          ← 통합관리 (UX/기획 담당)
```

### 협업 워크플로우

```
각 역할별 브랜치에서 작업
        ↓
Pull Request → main 머지
        ↓
통합 테스트 후 배포
```

---

## 디렉토리 구조

```
racoonDesk/
├── role-a/                  # 데이터 정제 영역 (Gemini)
│   ├── data/
│   │   ├── raw/             # 원본 인사관리 규정 파일
│   │   └── processed/       # 정제된 Markdown 파일
│   ├── test_sets/           # QA 테스트셋 (질문 20개 + 근거 조항)
│   └── guidelines/          # AI 답변 가이드라인
│
├── role-b/                  # RAG 파이프라인 (Claude)
│   ├── app/                 # Streamlit 앱
│   ├── rag/                 # RAG 핵심 로직
│   └── config/              # 설정 파일
│
└── role-c/                  # UX & 서비스 기획
    ├── ui/design/           # UI 설계 자료
    ├── reports/             # 성과 리포트
    └── feedback/            # 사용자 피드백 수집
```

---

## 시작하기

### 환경 설정

```bash
cd role-b
pip install -r requirements.txt
```

### 앱 실행

```bash
streamlit run role-b/app/main.py
```

---

## 커밋 컨벤션

```
[role-a] feat: 인사관리 규정 마크다운 정제 완료
[role-b] feat: 벡터 검색 로직 구현
[role-c] design: 메인 UI 와이어프레임 추가
```

- `feat` — 새 기능
- `fix` — 버그 수정
- `docs` — 문서
- `refactor` — 리팩토링
- `test` — 테스트
