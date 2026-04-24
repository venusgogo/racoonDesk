# 브랜치 보호 규칙 설정 가이드

CODEOWNERS가 실제로 작동하려면 GitHub 저장소 설정에서 브랜치 보호 규칙을 활성화해야 합니다.

## 설정 경로

`GitHub 저장소` → `Settings` → `Branches` → `Add branch ruleset`

## 각 브랜치별 권장 설정

### `claude/hr-policy-rag-system-cOm6x` (통합 브랜치)

| 옵션 | 값 |
|------|----|
| Require a pull request before merging | ✅ ON |
| Required approvals | 1 |
| Require review from Code Owners | ✅ ON |
| Require status checks to pass | 선택사항 |
| Do not allow bypassing the above settings | ✅ ON |

### `role-a/data-refinement`

| 옵션 | 값 |
|------|----|
| Require a pull request before merging | ✅ ON |
| Required approvals | 1 |
| Require review from Code Owners | ✅ ON |
| Restrict who can push | `@gemini-user` 만 허용 |

### `role-b/rag-pipeline`

| 옵션 | 값 |
|------|----|
| Require a pull request before merging | ✅ ON |
| Required approvals | 1 |
| Require review from Code Owners | ✅ ON |
| Restrict who can push | `@claude-user` 만 허용 |

### `role-c/ux-service`

| 옵션 | 값 |
|------|----|
| Require a pull request before merging | ✅ ON |
| Required approvals | 1 |
| Require review from Code Owners | ✅ ON |
| Restrict who can push | `@manager-user` 만 허용 |

## CODEOWNERS 적용 후 PR 흐름

```
Role A가 role-b/ 파일을 수정하려 할 때
        ↓
PR 생성 시 자동으로 @claude-user 리뷰 요청
        ↓
@claude-user approve 없이는 머지 불가
        ↓
사실상 폴더 단위 권한 분리 효과
```

## 주의사항

- CODEOWNERS는 파일이 **기본 브랜치(main 또는 통합 브랜치)** 에 있어야 작동합니다.
- `@username` 은 반드시 해당 저장소의 collaborator여야 합니다.
- Organization 사용 시 `@org/team-name` 형식으로 팀 단위 지정도 가능합니다.
