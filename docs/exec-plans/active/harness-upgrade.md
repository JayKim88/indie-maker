# Indie-Maker Harness 고도화 계획

> **출처**: OpenAI "Harness Engineering: leveraging Codex in an agent-first world" (2026-02-11, Ryan Lopopolo)
> **목적**: 아티클의 핵심 개념을 indie-maker에 적용 가능한 형태로 문서화하고 이행을 트래킹
> **관련 문서**: [`ROADMAP.md`](../../../ROADMAP.md) — Track 1 (Harness Hardening) / Track 2 (Agent Runtime)

---

## 1. 핵심 개념 참조

### C1 — AGENTS.md = Table of Contents, Not Encyclopedia

**원칙**: 단일 거대 명세서는 실패한다. 짧은 지도(~100줄) + 구조화된 `docs/`로 분리하라.

**실패 패턴 (monolithic)**

| 문제 | 결과 |
|---|---|
| Context 낭비 | 태스크·코드가 밀려남 |
| 모든 게 "중요" | 아무것도 중요하지 않음 |
| 즉시 rot | stale 규칙 묘지 |
| 검증 불가 | drift 필연적 |

**성공 패턴**
```
AGENTS.md        ← 지도 (~100줄, 포인터만)
docs/
├── design-docs/
│   └── core-beliefs.md    ← agent 운영 철학
├── exec-plans/
│   ├── active/            ← 실행 중
│   ├── completed/         ← 완료 이력
│   └── tech-debt-tracker.md
├── product-specs/
├── generated/
│   └── db-schema.md       ← 자동 생성 지식
├── QUALITY_SCORE.md       ← 도메인별 품질 등급
├── RELIABILITY.md
└── SECURITY.md
```

---

### C2 — Agent Legibility (가독성이 목표)

**원칙**: Agent가 context 내에서 접근할 수 없는 것은 사실상 존재하지 않는다.

```
[Slack 토론] [회의 결정] [사람 머릿속]
              ↓ 반드시 repo에 인코딩
         [repo 내 markdown]
```

→ 아키텍처 결정, 팀 컨벤션, 제품 철학 → 모두 repo에 커밋해야 agent가 활용 가능.

---

### C3 — Repository Knowledge as System of Record

**원칙**: Execution Plans는 first-class artifact — repo에 버전 관리.

```
exec-plans/
├── active/                ← 진행 중 계획 (progress + decision log 포함)
├── completed/             ← 완료 이력 (학습 자료)
└── tech-debt-tracker.md   ← 기술 부채 카탈로그
```

→ 계획이 repo에 있으면 agent가 직접 읽고, 과거 결정을 추적하고, 이어서 작업 가능.

---

### C4 — Layered Architecture + Mechanical Enforcement

**원칙**: 문서로 설명하지 말고, 린터로 강제하라. 경계는 중앙에서 강제, 구현은 로컬 자유.

```
도메인 레이어 예시:
Types → Config → Repo → Service → Runtime → UI
                                      ↑
              역방향 의존 → 커스텀 린터로 빌드 실패
```

→ indie-maker 적용: skill 산출물 경로, CLAUDE.md 규칙 → 린터/hook으로 기계적 강제.

---

### C5 — Ralph Wiggum Loop (Self-Review Loop)

**원칙**: Agent가 자신의 작업을 스스로 검토하고, 모든 reviewer가 통과할 때까지 반복한다.

```
[Agent 작업]
      ↓
[자기 검토 (local)]
      ↓
[Agent 리뷰 요청]
      ↓
[피드백 반영]
      ↓ (반복)
[모든 reviewer 통과 → 완료]
```

→ indie-maker 적용: 각 스킬의 마지막 단계에 self-critique 체크포인트 추가.

---

### C6 — Observability → Agent 가독화

**원칙**: 로그·메트릭·트레이스를 agent가 직접 쿼리할 수 있게 만들어라.

```
App → logs/metrics/traces
          ↓
      LogQL / PromQL / TraceQL
          ↓
      Agent가 직접 쿼리·검증
```

→ "서비스 startup 800ms 이내" 같은 목표를 agent가 직접 측정하고 달성.
→ indie-maker 적용 범위: 소규모이므로 Langfuse/LangSmith 수준이면 충분.

---

### C7 — Golden Principles + GC Agent

**원칙**: 기술 부채는 고금리 대출 — 매일 조금씩 갚는다. Human taste를 한 번 캡처하면 매일 강제.

```
Golden Principles (기계적으로 강제 가능한 opinionated 규칙)
          ↓
Recurring Cleanup Agent
  - 편차 스캔
  - stale 문서 감지
  - 리팩토링 PR 자동 생성 (1분 검토 후 auto-merge)
```

---

### C8 — Engineer Role Redefinition

**원칙**: 코드 작성 → 환경 설계 + 의도 명세 + 피드백 루프 구축.

뭔가 안 될 때 fix는 "try harder"가 아니라:
> "어떤 capability가 빠졌는지 파악해 agent가 인식 가능하게 만드는 것"

→ indie-maker 적용: 스킬이 실패하면 → 스킬 자체 개선이 아닌, 하네스(CLAUDE.md, knowledge, hook) 개선.

---

## 2. 갭 분석: indie-maker vs OpenAI 패턴

| OpenAI 패턴 | indie-maker 현재 | 갭 크기 | ROADMAP 연계 |
|---|---|---|---|
| AGENTS.md = 지도 (~100줄) | CLAUDE.md ~200줄+ encyclopedia | **크다** | L3.3 인접 |
| core-beliefs.md | 없음 (CLAUDE.md 내 산재) | **크다** | 신규 |
| exec-plans/ (active/completed/tech-debt) | 없음 | **크다** | 신규 |
| QUALITY_SCORE.md | 없음 | 중간 | 신규 |
| Self-review loop (스킬 내) | 없음 | 중간 | L5.1 인접 |
| 기계적 문서 검증 (CI 린터) | 없음 | 중간 | L5.2 |
| GC Agent (cleanup/doc-gardening) | 없음 | 중간 | L5.4 |
| 관측성 (agent 가독 로그/메트릭) | 없음 | 작다 (indie 규모) | T2.M2 |
| Knowledge = Repo (Slack/결정 → markdown) | 부분적 (wrap-up/에 있음) | 작다 | 습관 변경 |

---

## 3. 고도화 체크리스트

> **상태 기호**: `[ ]` 미착수 | `[~]` 진행 중 | `[x]` 완료 | `[-]` 보류

---

### Tier 1 — 즉시 적용 가능 (구조 변경, 코드 없음)

#### T1-A. CLAUDE.md 슬림화

- [ ] CLAUDE.md를 100줄 이하 지도로 축소
  - 스프린트 맵, 스킬 레퍼런스 테이블, 핵심 원칙 포인터만 유지
  - 세부 내용 → `docs/` 하위 파일로 이동
- [ ] 스킬별 상세 설명 → `docs/skill-specs/` 또는 각 skill.md로 이동
- **검증**: CLAUDE.md < 120줄, 모든 스킬 기능 동등 확인

#### T1-B. `docs/core-beliefs.md` 신설

- [ ] indie-maker 운영 철학 문서화:
  - Kill criteria first
  - Pre-sale before build
  - One core flow only
  - Automate after $100 MRR
  - Kill = data, not failure
- [ ] 모든 스킬이 시작 시 참조하도록 AGENTS.md(CLAUDE.md)에 포인터 추가
- **목적**: 스프린트 원칙이 agent가 읽을 수 있는 형태로 존재

#### T1-C. `docs/exec-plans/` 구조 신설

- [x] `docs/exec-plans/active/` — 현재 진행 중인 실행 계획 (2026-05-26)
- [x] `docs/exec-plans/completed/` — 완료 이력 (학습 자료) (2026-05-26)
- [ ] `docs/exec-plans/tech-debt-tracker.md` — 기술 부채 카탈로그
- [x] 첫 exec-plan으로 본 문서(`harness-upgrade.md`)를 `active/`로 이동 (2026-05-26)
- [ ] `ROADMAP.md`의 진행 중 항목을 exec-plan 형식으로 마이그레이션 (선택 — ROADMAP은 루트 유지)
- **목적**: agent가 "지금 뭘 하고 있는지"를 repo에서 직접 파악 가능

#### T1-D. `docs/QUALITY_SCORE.md` 신설

- [ ] 각 스킬/phase별 품질 등급 테이블:
  ```
  | 스킬 | 산출물 완성도 | Self-review 여부 | 마지막 갱신 |
  |---|---|---|---|
  | indie-planner | ★★★☆☆ | ✗ | — |
  ```
- [ ] 스킬 실행 후 해당 행 업데이트 권장 (자동화 전 수동)
- **목적**: drift 추적 + 개선 우선순위 가시화

---

### Tier 2 — 스킬 레벨 강화 (스킬 파일 수정)

#### T2-A. Self-review Loop (Ralph Wiggum 패턴)

각 스킬의 마지막 단계에 self-critique 체크포인트 추가.

- [ ] **indie-planner** (Reid): idea-canvas.md 완성 후 자가 검토
  - 검토 기준: Kill criteria 명시 여부, 경쟁사 분석 충분성, pre-sale 조건 설정
- [ ] **indie-ux** (Kai): ux-flow.md 완성 후 자가 검토
  - 검토 기준: 핵심 플로우 1개만 커버했는지, Nielsen 10 heuristics 체크
- [ ] **indie-analyst** (Nova): kill-go-report.md 완성 후 자가 검토
  - 검토 기준: 데이터 기반 판단인지, Kill/Go 기준이 D1 설정과 일치하는지
- [ ] 우선 3개 스킬 적용 후 나머지 확장

**패턴 구조**:
```
## Self-Review Checkpoint (스킬 마지막 단계)

다음 기준을 스스로 검토하라:
1. [기준 A] — 충족 여부: Yes/No → No면 [수정 지시]
2. [기준 B] — 충족 여부: Yes/No → No면 [수정 지시]
3. [기준 C] — 충족 여부: Yes/No → No면 [수정 지시]

모든 기준 통과 시에만 산출물 최종 저장.
```

#### T2-B. Cross-Skill Validation

- [ ] 스킬 시작 시 이전 단계 산출물 completeness 자동 체크
  - indie-ux 시작 → `docs/indie-planner/idea-canvas.md` 존재 + 필수 섹션 확인
  - indie-architect 시작 → `docs/indie-designer/design-brief.md` 존재 확인
- [ ] 미충족 시: "이전 스킬 산출물이 불완전합니다. [스킬명] 먼저 완료하세요." 출력
- **목적**: 스프린트 phase 순서 기계적 보장

#### T2-C. Skill Outcome Template 표준화

- [ ] 각 스킬 산출물의 필수 섹션 정의 (schema 수준)
  - indie-planner: `## 문제정의`, `## 타겟`, `## Kill Criteria`, `## 경쟁사` 필수
  - indie-analyst: `## 판정`, `## 근거 데이터`, `## 다음 행동` 필수
- [ ] QUALITY_SCORE.md의 "완성도" 평가 기준으로 활용

---

### Tier 3 — 자동화 (코드/hook/새 스킬)

#### T3-A. `indie-cleanup` 스킬 (GC Agent 개념)

- [ ] 신규 `/indie-cleanup` 스킬 설계
  - 모든 `projects/*/docs/` 스캔
  - 불일치·stale 항목 감지:
    - `.indie-sprint.json`의 `completed_skills`와 실제 파일 불일치
    - 오래된 metrics (last_updated > 7일)
    - 빈 docs 디렉토리
  - 리포트 출력 + 수정 제안
- [ ] ROADMAP.md L5.4 (Garbage Collection)와 통합
- **트리거**: 스프린트 주간 리뷰 시 수동 실행

#### T3-B. Sprint State Machine 정교화

- [ ] ROADMAP.md L2.4 (스킬 종료 시 자동 업데이트) 완료
- [ ] `.indie-sprint.json` 변경 이력을 `docs/exec-plans/` 에 자동 반영
- [ ] `current_phase` 변경 시 `docs/exec-plans/active/` 에 progress 업데이트

#### T3-C. Doc-Gardening CI

- [ ] ROADMAP.md L5.2 (Fitness Functions) 기반
- [ ] GitHub Actions workflow 또는 `bin/fitness-check.py`:
  - 필수 섹션 존재 여부 검증
  - Cross-link 유효성 검증 (참조 파일 존재 여부)
  - QUALITY_SCORE.md freshness 체크 (> 14일이면 경고)
- [ ] pre-commit hook으로 로컬 실행

#### T3-D. Knowledge → Repo 습관 강화

- [ ] 모든 아키텍처 결정/중요 토론 → `docs/design-docs/` 에 ADR(Architecture Decision Record) 형식으로 기록
  - 템플릿: `## 맥락`, `## 결정`, `## 결과`, `## 대안`
- [ ] `docs/design-docs/index.md` 신설 (검증 상태 포함)
- **목적**: Slack/세션에 산재된 결정들을 agent 가독 형태로 보존

---

## 4. 우선순위 결정 기준

```
임팩트 = (Context 품질 개선 × 스프린트 속도 향상) / 구현 비용
```

| 항목 | 임팩트 | 비용 | 우선순위 |
|---|---|---|---|
| T1-A CLAUDE.md 슬림화 | ★★★★★ | 1h | **P0** |
| T1-B core-beliefs.md | ★★★★☆ | 0.5h | **P0** |
| T1-C exec-plans/ 구조 | ★★★☆☆ | 0.5h | **P1** |
| T2-A Self-review Loop (3 스킬) | ★★★★☆ | 2h | **P1** |
| T2-B Cross-Skill Validation | ★★★☆☆ | 1.5h | **P2** |
| T1-D QUALITY_SCORE.md | ★★★☆☆ | 0.5h | **P2** |
| T3-A indie-cleanup 스킬 | ★★★☆☆ | 3h | **P3** |
| T3-C Doc-Gardening CI | ★★★☆☆ | 2h | **P3** |
| T3-D ADR 습관 | ★★☆☆☆ | 습관 | **P3** |

---

## 5. ROADMAP.md 연계 매핑

| 본 문서 항목 | ROADMAP.md 연계 |
|---|---|
| T1-A CLAUDE.md 슬림화 | L3.3 (스킬 파일 다이어트)와 병행 가능 |
| T2-A Self-review Loop | **L5.1** Lint-as-Prompt Pattern의 일부 |
| T3-A indie-cleanup | **L5.4** Garbage Collection — Drift Detection |
| T3-C Doc-Gardening CI | **L5.2** Framework Fitness Functions |
| T3-B Sprint State Machine | **L2.4** + **T2.M1.3** |
| T1-C exec-plans/ | **T2.M1.3** portfolio DB와 연동 고려 |

> **원칙**: 본 문서의 체크리스트는 ROADMAP.md의 Layer/Milestone과 중복되지 않는 신규 항목 중심.
> 기존 트래킹은 ROADMAP.md를 정본으로 한다.

---

## 6. 진행 로그

| 날짜 | 항목 | 내용 |
|---|---|---|
| 2026-05-17 | 문서 초안 | OpenAI Harness Engineering 개념 매핑 + 고도화 체크리스트 작성 |

---

## 참조

- [OpenAI Harness Engineering (2026-02-11)](https://openai.com/index/harness-engineering/)
- [ROADMAP.md](../../../ROADMAP.md) — Track 1 (Harness Hardening) + Track 2 (Agent Runtime)
- [indie-sprint-playbook.md](../../indie-sprint-playbook.md) — 스프린트 마스터 가이드
- [docs/agent-runtime/README.md](../../agent-runtime/README.md) — Agent Runtime Layer 정의
