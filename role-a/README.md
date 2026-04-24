# Role A — 데이터 정제 및 도메인 전문가

담당 AI: **Gemini**

## 임무

AI가 정확하게 규정을 읽을 수 있도록 원천 데이터를 최적화하고 검증합니다.

## 작업 목록

- [ ] 인사관리 규정 원본 파일 수집 (`data/raw/`)
- [ ] 불필요한 태그 제거 및 Markdown 변환 (`data/processed/`)
- [ ] 실사용자 질문 20개 생성 + 근거 조항 매핑 (`test_sets/`)
- [ ] AI 답변 가이드라인 작성 및 검증 (`guidelines/`)

## 디렉토리 구조

```
role-a/
├── data/
│   ├── raw/            ← 원본 규정 파일 (PDF, HWP, DOCX 등)
│   └── processed/      ← 정제된 Markdown 파일
├── test_sets/
│   ├── questions.json  ← 질문 20개
│   └── answers.json    ← 근거 조항 포함 정답
└── guidelines/
    └── answer_policy.md ← AI 답변 가이드라인
```

## 데이터 정제 기준

1. **태그 제거**: HTML, XML 등 불필요한 마크업 제거
2. **조항 구조 보존**: 제N조 형식을 반드시 유지
3. **계층 구조**: `#`, `##`, `###` 헤더로 장/절/조항 구분
4. **특수문자**: 법령 특수문자 통일 처리

## 테스트셋 형식

```json
{
  "id": 1,
  "question": "연차 유급휴가는 며칠인가요?",
  "answer": "입사 1년 미만 시 월 1일, 1년 이상 시 15일입니다.",
  "reference": "제12조 제1항",
  "category": "휴가"
}
```

## 커밋 예시

```bash
git checkout role-a/data-refinement
git add role-a/data/processed/hr_policy.md
git commit -m "[role-a] feat: 인사관리 규정 1~5장 마크다운 정제"
git push origin role-a/data-refinement
```
