# Role C — 서비스 기획 및 실무 UX 관리자

담당: **통합 관리**

## 임무

최종 사용자인 직원들이 편리하게 사용할 수 있도록 서비스 외관을 설계하고 성과를 관리합니다.

## 작업 목록

- [ ] RACOON 메인 UI 와이어프레임 설계 (`ui/design/`)
- [ ] 사용자 테스트 시나리오 작성
- [ ] 팀원 대상 사용자 테스트 진행 및 피드백 수집 (`feedback/`)
- [ ] Role B에 피드백 전달 및 개선 추적
- [ ] 도입 전후 업무 효율성 측정
- [ ] 프로젝트 성공 사례 1페이지 리포트 작성 (`reports/`)

## 디렉토리 구조

```
role-c/
├── ui/
│   └── design/
│       ├── wireframe.md      ← UI 와이어프레임 명세
│       └── style_guide.md    ← 디자인 가이드 (색상, 폰트)
├── feedback/
│   ├── test_scenarios.md     ← 사용자 테스트 시나리오
│   └── feedback_log.md       ← 피드백 수집 로그
└── reports/
    └── success_report.md     ← 1페이지 성공 사례 리포트
```

## 사용자 테스트 체크리스트

- [ ] 파일 업로드 UX (직관성)
- [ ] 질문 입력 편의성
- [ ] 답변 가독성 (조항 번호 표시)
- [ ] 오답/무응답 처리 경험
- [ ] 모바일 환경 대응

## 피드백 → B 전달 형식

```markdown
## 피드백 #001
- 날짜: YYYY-MM-DD
- 테스터: N명
- 문제: [문제 내용]
- 우선순위: 높음/중간/낮음
- 개선 제안: [내용]
```

## 커밋 예시

```bash
git checkout role-c/ux-service
git add role-c/ui/design/wireframe.md
git commit -m "[role-c] design: 메인 화면 와이어프레임 초안 추가"
git push origin role-c/ux-service
```
