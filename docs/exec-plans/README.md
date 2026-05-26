# Execution Plans

하네스(프레임워크) 자체에 대한 실행 계획(execution plan)을 보관하는 곳.
OpenAI "Harness Engineering" 패턴 C3 (Repository Knowledge as System of Record) 적용.

> **대상**: 프레임워크 개선 작업. 개별 프로젝트의 sprint 산출물은 `projects/{name}/docs/`에 보관.

---

## 구조

```
docs/exec-plans/
├── active/        ← 진행 중인 실행 계획
├── completed/     ← 완료 이력 (학습 자료)
└── README.md
```

## 정본 vs 보조

| 문서 | 위치 | 역할 |
|---|---|---|
| `ROADMAP.md` | 루트 | **정본** — Track 1/2 진행 추적 (DONE/TODO 체크박스) |
| `docs/exec-plans/active/*.md` | 본 폴더 | 보조 — 외부 개념 적용·확장 체크리스트 |

→ exec-plan은 ROADMAP의 특정 Layer/Milestone과 연계되며, 중복 추적은 피한다.
중복이 발생하면 ROADMAP을 정본으로 보고 exec-plan을 보조로 취급한다.

## 라이프사이클

1. **신규 작성**: `active/{slug}.md` 로 생성. ROADMAP과의 연계 매핑을 본문에 명시.
2. **진행**: 체크리스트 갱신, 진행 로그 섹션에 날짜별 기록.
3. **완료**: `completed/{slug}.md`로 이동. 마지막에 "회고/학습" 섹션 추가.

## 현재 active

- [`track-1-harness-hardening.md`](active/track-1-harness-hardening.md) — v0.1 릴리스 트래커 (L0-L5)
- [`track-2-agent-runtime.md`](active/track-2-agent-runtime.md) — v0.2 릴리스 트래커 (M1-M5)
- [`harness-upgrade.md`](active/harness-upgrade.md) — OpenAI Harness Engineering 개념 매핑 (보조)
