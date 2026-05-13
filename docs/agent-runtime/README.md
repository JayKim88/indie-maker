# Agent Runtime Layer

> 스프린트가 살아 움직이는 동안 **상태를 읽고 도구를 써서 판단·행동하는** 에이전트 계층
> 작성: 2026-05-13 | 상태: 기획 단계 (빌드 미시작)

---

## 한 줄 정의

> **Agent Runtime** = 14개 build-time skill 옆에 추가되는 *런타임 관제 계층*.
> Build-time skill이 "스프린트의 산출물을 만든다"면, Agent Runtime은 "스프린트가 돌아가는 중에 데이터를 보고 행동한다."

---

## 14 Skills와의 대비

| 축 | 14 Skills (`skills/indie-*`) | Agent Runtime (`docs/agent-runtime/`) |
|---|---|---|
| **시점** | Build-time (한 phase 단위) | Runtime (always-on) |
| **호출 방식** | 사용자가 명시 호출 (`/indie-planner`) | 자가 라우팅 (`/mission-control "..."`) |
| **출력** | 산출물 마크다운 (`docs/indie-*/...md`) | 액션·판단·종합 리포트 |
| **데이터** | 사용자가 인터뷰로 제공 | tool로 직접 fetch (state, GitHub, Stripe, DB) |
| **상태** | stateless (각 phase 독립) | stateful (sprint live state 관찰) |

핵심은 **"빌드 vs 운영" 분리**다. Build-time agent가 스프린트의 *제작자* 라면, Runtime agent는 스프린트의 *관제사*다.

---

## 4개 컴포넌트

| 컴포넌트 | 한 줄 정의 | 비유 |
|---|---|---|
| **agent-runtime** | 스프린트 실행 중 상태를 읽고 도구로 행동하는 에이전트 계층 (전체) | 관제실 |
| **indie-mcp** | 스프린트 상태와 외부 시스템을 LLM이 호출 가능한 tool로 노출하는 MCP 서버 | 손·눈 |
| **text-to-sql** | 자연어 질문을 안전한 read-only SQL로 변환해 portfolio DB에서 답을 찾는 tool | 기억 |
| **mission-control** | tool과 sub-agent를 자동 조합·병렬 dispatch해 종합 판단·다음 액션을 내리는 runtime orchestrator | 뇌 |

---

## 동작 다이어그램

```
사용자 질문 (자연어)
   ↓
┌────────────────────────────────────────────────┐
│  mission-control  (뇌 — 판단)                  │
│                                                │
│  ├─ indie-mcp 호출 ─→ (손/눈)                  │
│  │   ├─ get_sprint_state()                     │
│  │   ├─ github_stats()                         │
│  │   ├─ stripe_revenue()                       │
│  │   └─ plausible_traffic()                    │
│  │                                             │
│  ├─ text-to-sql 호출 ─→ (기억)                 │
│  │   └─ query_portfolio("과거 비슷한 sprint")  │
│  │                                             │
│  └─ sub-agent 병렬 dispatch                     │
│      ├─ Performance Assessor ──┐               │
│      ├─ Risk Assessor          ├→ Synthesizer  │
│      └─ Trajectory Assessor ───┘               │
└────────────────────────────────────────────────┘
   ↓
종합 verdict + 다음 액션
```

---

## 빌드 순서

| # | 빌드 | 산출물 | 예상 비용 | 의존성 |
|---|------|--------|----------|--------|
| **1** | `indie-mcp` MCP 서버 | Python FastMCP 서버 + tool 10개 | 1-2일 | 없음 |
| **2** | `text-to-sql` tool | indie-mcp에 tool 1개 추가 | 0.5일 | #1, portfolio DB 결정 |
| **3** | `mission-control` orchestrator | Python + Anthropic SDK | 1-2일 | #1, (선택적으로 #2) |
| 4 (선택) | Phase 3 Parallel Build | 별도 모듈, Mission Control sub-orchestrator | 1일 | #3 |

**총 추정**: 3-4일 (선택 빌드 제외). 풀 코스는 4-5일.

---

## 핵심 설계 원칙

| 원칙 | 내용 |
|---|---|
| **Tool boundary = security boundary** | 모든 외부 시스템 접근은 indie-mcp tool로만. 직접 API 호출 금지. |
| **Read-only by default** | 상태 변경 tool은 명시적 confirmation 필요. text-to-sql은 항상 read-only + whitelist. |
| **Stateless tools, stateful orchestrator** | tool은 idempotent. 상태는 mission-control이 보유. |
| **Single source of truth** | sprint 상태는 portfolio DB 1곳. JSON ↔ Supabase 동기화는 hook으로. |
| **Parallel where safe, sequential where ordered** | sub-agent 판단은 병렬, 액션 실행은 순차. |

---

## Open Questions

### Resolved

- **Q1 — portfolio DB = ?** → ✅ **SQLite 단일 파일 + PostToolUse 동기화 hook** (결정: 2026-05-13)
  - 위치: `portfolio.db` (repo root, `.gitignore` 대상)
  - 동기화: `.indie-sprint.json` 변경 시 → SQLite mirror (HARNESS-TODO L2.4 확장)
  - 마이그레이션: 초기 seed는 기존 6개 `.indie-sprint.json` 에서 1회 일괄 import
  - 결정 근거: 정당화 use case = *"내가 항상 어느 Phase에서 막히는가?"* + 자유 SQL 자유도 보존
  - 대안 기각: Supabase (network 의존 + 개인용 과잉), JSON glob (use case #2-4의 SQL 자유도 안 됨)

### Pending

| # | 질문 | 영향 |
|---|------|------|
| Q2 | indie-mcp 인증 방식 — local-only / API key / Supabase JWT 재사용? | 보안 모델, OS 공개 시 안전성 |
| Q3 | mission-control은 별도 skill (`/mission-control`)인가 새 CLI 진입점인가? | 사용자 경험, Claude Code 통합 방식 |
| Q4 | 외부 통합 tool 우선순위 — GitHub / Stripe / Plausible / Product Hunt 중 어느 것부터? | Build #1 범위 |
| Q5 | sub-agent 모델 선택 — 모두 Opus / Synthesizer만 Opus + 나머지 Sonnet / 다른 조합? | 비용 vs 품질 |
| **Q6** | **portfolio.db 스키마 — 어떤 테이블/컬럼?** | Build #2 직접 블로커. `projects` / `phase_transitions` / `metrics` / `skill_calls` / `lessons` 5개 테이블 초안 필요 |

---

## 기존 자산과의 관계

| 자산 | 위치 | 관계 |
|---|------|------|
| 14 skills | `skills/indie-*/SKILL.md` | Agent Runtime은 **이 위에 얹는 layer**. 기존 skill 동작 변경 없음. |
| `.indie-sprint.json` | `projects/*/.indie-sprint.json` | indie-mcp의 `get_sprint_state()` 가 읽는 주된 소스. |
| HARNESS-TODO L2.4 (PostToolUse hook) | `HARNESS-TODO.md` | portfolio DB 하이브리드 채택 시 이 항목 확장. |
| `bin/inject-sprint-context.py` | `bin/` | SessionStart에서 컨텍스트 주입. Mission Control 도 같은 방식 재사용 가능. |
| 지식 가이드 (frontend/backend/infra 등) | `knowledge/*.md` | sub-agent의 system prompt에 selective inject. |

---

## 컴포넌트별 상세 스펙 (TBD)

빌드 시작 전 각 컴포넌트별로 별도 스펙 문서 작성 예정:

- [`indie-mcp-spec.md`](./indie-mcp-spec.md) — Tool 카탈로그, 인증, 에러 모델, MCP 서버 구조
- [`text-to-sql.md`](./text-to-sql.md) — 스키마 화이트리스트, SQL injection 방어, 쿼리 예시
- [`mission-control.md`](./mission-control.md) — 파이프라인 단계, sub-agent 정의, conflict resolution
- [`roadmap.md`](./roadmap.md) — 마일스톤, 검증 기준, dogfooding 계획

---

## 변경 이력

- **2026-05-13**: 초안 작성 (기획 단계, 빌드 미시작)
