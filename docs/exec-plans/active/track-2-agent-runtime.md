# Track 2 — Agent Runtime Layer

> **베이스**: [`../../agent-runtime/README.md`](../../agent-runtime/README.md) — layer 정의 + 4 컴포넌트 + 빌드 순서
> **궁극 목적**: indie-maker가 sprint 반복을 통해 *사용자에 대해* 학습하는 메타-프레임워크로 진화. 매번 다른 이유로 실패한다고 느끼지만 실제론 같은 패턴 반복인 경우를 데이터로 반증.
> **정당화 use case**: "내가 항상 어느 phase에서 막히는가?" (self-diagnosis ⭐⭐⭐⭐⭐)
> **소속 릴리스**: v0.2 — Agent Runtime Layer (`../../../ROADMAP.md`)

---

## 진행 요약

| Milestone | 주제 | 작업 수 | 누적 비용 | 상태 |
|-----------|------|--------|----------|------|
| M1 | Portfolio DB Foundation (SQLite + sync) | 3 | ~1d | TODO |
| M2 | indie-mcp Server (sprint state + 외부 통합 + 분석 tool) | 4 | ~1-2d | TODO |
| M3 | text-to-sql tool (read-only + 화이트리스트) | 1 | ~0.5d | TODO |
| M4 | Mission Control (orchestrator + parallel sub-agents) | 3 | ~1-2d | TODO |
| M5 | Phase 3 Parallel Build (선택) | 3 | ~1d | DEFER |

**총 추정**: 3-4d (M5 제외)

---

## Open Questions

- ~~**RQ1**: portfolio DB form factor~~ → **해결됨 2026-05-13** (SQLite + PostToolUse 동기화)
- **RQ2**: indie-mcp 인증 방식 (local-only / API key / Supabase JWT 재사용?)
- **RQ3**: mission-control 진입점 (별도 skill / 새 CLI / 양쪽?)
- **RQ4**: 외부 통합 tool 우선순위 (GitHub / Stripe / Plausible / PH 중 어느 것부터?)
- **RQ5**: sub-agent 모델 선택 (전체 Opus / Synthesizer만 Opus + 나머지 Sonnet / 다른 조합?)
- **RQ6**: portfolio.db 스키마 (5개 테이블 — `projects`/`phase_transitions`/`metrics`/`skill_calls`/`lessons` — 컬럼·관계·인덱스 초안)

---

## Milestone 1 — Portfolio DB Foundation (~1d)

### M1.1 SQLite 스키마 정의 [TODO, ~1-2h]
- [ ] `schemas/portfolio.sql` — DDL (5 테이블: `projects` / `phase_transitions` / `metrics` / `skill_calls` / `lessons`)
- [ ] 인라인 주석으로 컬럼 의도·정규화 결정 표현
- [ ] (선택) `docs/agent-runtime/portfolio-db-design.md` — 정규화·동기화 semantics 의사결정 메모
- **Acceptance**: `sqlite3 portfolio.db < schemas/portfolio.sql` 무에러
- **Depends**: RQ6 해소

### M1.2 초기 Seed 스크립트 [TODO, ~1h]
- [ ] `bin/seed-portfolio-db.py` — 6개 `.indie-sprint.json` → SQLite 일괄 import
- [ ] `phase_transitions` 백필 — `completed_skills` 배열로부터 전이 이력 추론
- **Acceptance**: `portfolio.db` 에 projects 6 rows + phase_transitions 다중 rows
- **Depends**: M1.1

### M1.3 PostToolUse 동기화 hook [TODO, ~2-3h]
- [ ] **T1.L2.4 확장** — `.indie-sprint.json` 변경 시 `portfolio.db` mirror
- [ ] 양방향 일관성 검증 (mismatch 시 JSON을 진실로)
- **Acceptance**: JSON 수정 → SQLite 자동 반영 verified
- **Depends**: M1.1, M1.2, T1.L2.4

---

## Milestone 2 — indie-mcp Server (~1-2d)

### M2.1 MCP 서버 스캐폴딩 [TODO, ~2h]
- [ ] `agent-runtime/mcp/` 디렉토리 + FastMCP 의존성
- [ ] `agent-runtime/mcp/server.py` 부트스트랩
- [ ] Claude Code에 MCP 서버 등록 절차 문서화
- **Acceptance**: ping tool 호출 정상

### M2.2 내부 sprint state tools [TODO, ~3h]
- [ ] `get_sprint_state(project)`, `list_artifacts(project)`, `read_artifact(name)`
- [ ] `record_metric(project, name, value)`, `advance_phase(project, to_phase)` (state machine 검증 포함)
- **Acceptance**: 5 tool 호출 정확한 결과
- **Depends**: M2.1

### M2.3 외부 통합 tools [TODO, ~4-6h]
- [ ] 우선순위 결정 (RQ4)
- [ ] 최소 2개 시스템 wrap (후보: GitHub, Stripe, Plausible, Product Hunt)
- **Acceptance**: 외부 데이터 정확한 fetch
- **Depends**: M2.1, RQ4

### M2.4 분석 tools (use case 1-4) [TODO, ~2-3h]
- [ ] `get_phase_distribution()` — use case #1 (정당화 use case)
- [ ] `get_lesson_frequency()` — use case #2
- [ ] `get_personal_baseline(metric)` — use case #3
- [ ] `get_skill_usage()` — use case #4
- **Acceptance**: 4 use case 모두 답 가능
- **Depends**: M1.1 (스키마), M2.1

---

## Milestone 3 — text-to-sql tool (~0.5d)

### M3.1 `query_portfolio` MCP tool [TODO, ~3-4h]
- [ ] LLM SQL 생성 → safety check → read-only execution
- [ ] 화이트리스트 (테이블/컬럼), timeout, row limit, SELECT-only enforcement
- [ ] SQL injection / write 시도 회귀 테스트
- **Acceptance**: 임의 자연어 → 안전한 SQL → 정확한 결과. write/DROP 시도 거부 verified
- **Depends**: M1.1, M2.1

---

## Milestone 4 — Mission Control (~1-2d)

### M4.1 orchestrator 스캐폴딩 [TODO, ~2h]
- [ ] `agent-runtime/mission-control/` 진입점
- [ ] 진입 방식 결정 (RQ3) — skill / CLI / 양쪽
- **Acceptance**: 명령 → tool 호출 → 응답 최소 흐름 동작

### M4.2 sub-agent 병렬 dispatch [TODO, ~3h]
- [ ] Performance Assessor / Risk Assessor / Trajectory Assessor 3 sub-agent
- [ ] `asyncio.gather` 로 Anthropic API 병렬 호출
- [ ] Synthesizer agent로 결과 merge
- **Acceptance**: 3 sub-agent 동시 실행 → 통합 verdict
- **Depends**: M4.1, RQ5

### M4.3 use case 통합 시나리오 [TODO, ~2h]
- [ ] "이번 sprint Kill/Go 어떻게 봐?" — 종합 답 동작
- [ ] "어디서 막히는지 봐줘" — use case #1 자가 진단
- **Acceptance**: 2 시나리오 end-to-end 동작
- **Depends**: M2 전체, M3, M4.2

---

## Milestone 5 — Phase 3 Parallel Build (선택, ~1d) [DEFER]

### M5.1 architecture.md 파서 [DEFER, ~2h]
### M5.2 Rex/Axel/Sam 병렬 dispatch [DEFER, ~3h]
### M5.3 Arch contract verifier [DEFER, ~2h]

**의존성 순서**: M1 → (M2 병렬 가능, 단 M2.4는 M1 후) → M3 → M4 → M5

---

## Cross-Track Dependencies (Track 1 연계)

| Track 1 항목 | Track 2 항목 | 관계 |
|---|---|---|
| **T1.L2.4** PostToolUse hook | **T2.M1.3** SQLite sync hook | T2.M1.3은 T1.L2.4의 자연 확장 — 함께 진행 권장 |
| **T1.L5.5** Cycle-Learning Constraint Injection | **T2.M2.4** `get_lesson_frequency()` | T1.L5.5의 YAML constraint 가 T2.M2.4 분석 tool의 데이터 풍부도에 기여 |
| **T1.L5.2** Framework Fitness Functions | **T2.M1.1** SQLite 스키마 | T1.L5.2의 일관성 검증 범위에 SQL 스키마 포함 가능 |
| **T1.L2.1** `.indie-sprint.json` 스키마 | **T2.M1.1** SQL 스키마 | JSON ↔ SQL 매핑 — 두 스키마가 호환되어야 함 |

→ Track 1 상세: [`./track-1-harness-hardening.md`](./track-1-harness-hardening.md)

---

## Next Recommended Action

현재 시점 (2026-05-13 기준) 우선순위:

1. **T2.M1.1** — Portfolio DB 스키마 정의 (block 거의 모든 T2 작업) ⭐⭐⭐⭐⭐
2. **T1.L5.1** — Lint-as-Prompt Pattern (L5 후속의 베이스) ⭐⭐⭐⭐
3. **T2.M1.2 + T1.L2.4** — Seed + sync hook 통합 진행 (cross-track 시너지) ⭐⭐⭐⭐
4. **T2.M2.1 + T2.M2.2** — indie-mcp 기본 동작 (T2.M1과 병렬 가능) ⭐⭐⭐⭐

---

## 참조

- [`../../../ROADMAP.md`](../../../ROADMAP.md) — 릴리스 마일스톤 (v0.2)
- [`../../agent-runtime/README.md`](../../agent-runtime/README.md) — layer 정의, 4 컴포넌트, 빌드 순서, 동작 다이어그램
- [`../../../wrap-up/indie-maker-harness.md`](../../../wrap-up/indie-maker-harness.md) — 의사결정 이력 (portfolio DB 결정, use case 정당화)
- [`./track-1-harness-hardening.md`](./track-1-harness-hardening.md) — Track 1 (Harness Hardening) 상세
