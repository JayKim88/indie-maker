# Indie-Maker Roadmap

> **통합 작업 추적 문서** — Harness Hardening + Agent Runtime Layer 두 트랙을 한 곳에서 관리.
> 작성: 2026-05-12 (HARNESS-TODO 베이스) | 통합 재구조화: 2026-05-13 (Track 2 추가)

---

## 진행 요약

### Track 1 — Harness Hardening (프레임워크 품질·이식성)

| Layer | 주제 | 작업 수 | 누적 비용 | 상태 |
|-------|------|--------|----------|------|
| L0 | knowledge 정리 (orphan 격리) | 1 | 완료 | **DONE 2026-05-12** |
| L1 | Critical 버그 수정 | 3 | ~1시간 | **DONE 2026-05-12** |
| L2 | 스프린트 상태 머신 (핵심 ROI) | 4 | ~반나절 | **3.5/4 DONE** |
| L3 | Scope & Discipline 자동화 | 3 | ~3시간 | TODO |
| L4 | Speculative (보류) | 2 | — | DEFER |
| L5 | Self-Correcting & Behavior Harness + OS Readiness | 7 | ~10.5h | **1/7 DONE** (plan: `~/.claude/plans/bubbly-toasting-raccoon.md`) |

### Track 2 — Agent Runtime Layer (메타학습 capability)

| Milestone | 주제 | 작업 수 | 누적 비용 | 상태 |
|-----------|------|--------|----------|------|
| M1 | Portfolio DB Foundation (SQLite + sync) | 3 | ~1d | TODO |
| M2 | indie-mcp Server (sprint state + 외부 통합 + 분석 tool) | 4 | ~1-2d | TODO |
| M3 | text-to-sql tool (read-only + 화이트리스트) | 1 | ~0.5d | TODO |
| M4 | Mission Control (orchestrator + parallel sub-agents) | 3 | ~1-2d | TODO |
| M5 | Phase 3 Parallel Build (선택) | 3 | ~1d | DEFER |

**총 추정**: 3-4d (M5 제외) | **궁극 목적**: indie-maker가 sprint 반복을 통해 사용자에 대해 학습하는 메타-프레임워크로 진화 (`docs/agent-runtime/README.md` 참조)

---

## Open Questions (Cross-cutting)

### Track 1 (Harness)
- ~~**Q1**: `projects/` 아래 6개 활성/dormant/killed 분류~~ → **해결됨** (L2.1.1)
- ~~**Q2**: 스킬 source-of-truth~~ → **해결됨** (L1.1, project repo)
- ~~**Q3**: 첫 작업 Layer~~ → **해결됨** (L2 우선 진행됨)
- ~~**Q4**: docs/ 경로 정책~~ → **해결됨** (CLAUDE.md Skill Scope 섹션)
- ~~**Q5**: knowledge/ 신규 파일 처리~~ → **해결됨** (L0)

### Track 2 (Agent Runtime) — `docs/agent-runtime/README.md` 참조
- ~~**RQ1**: portfolio DB form factor~~ → **해결됨 2026-05-13** (SQLite + PostToolUse 동기화)
- **RQ2**: indie-mcp 인증 방식 (local-only / API key / Supabase JWT 재사용?)
- **RQ3**: mission-control 진입점 (별도 skill / 새 CLI / 양쪽?)
- **RQ4**: 외부 통합 tool 우선순위 (GitHub / Stripe / Plausible / PH 중 어느 것부터?)
- **RQ5**: sub-agent 모델 선택 (전체 Opus / Synthesizer만 Opus + 나머지 Sonnet / 다른 조합?)
- **RQ6**: portfolio.db 스키마 (5개 테이블 — `projects`/`phase_transitions`/`metrics`/`skill_calls`/`lessons` — 컬럼·관계·인덱스 초안)

---

# Track 1 — Harness Hardening (L0-L5)

> **베이스**: 실사용 분석 (skills 동기화 상태, docs 경로 누수, 6-프로젝트 병렬 운영)
> **목적**: 텍스트 약속에 의존하던 부분을 하네스 레이어(hooks/scripts/statusline)로 자동화하고, 부서진 부분을 수선

## Layer 0 — knowledge/ 정리 (완료)

### L0.1 신규 knowledge 파일 격리 [DONE — 2026-05-12]

**Why**
knowledge/에 indie 스택 외 자료 5개(`frontend-guide-general.md`, `frontend-guide-principles.md`, `frontend-guide-principles-ko.md`, `backend-guide-principles.md` + 미완성 한글 번역)가 떠다님. SKILL은 모두 indie 스택 `*-guide.md` + `full-stack-*.md`만 참조.

**Done**
- [x] `knowledge/senior-reference/` 폴더 생성
- [x] `frontend-guide-general.md` → `senior-reference/frontend-senior-guide.md` (rename + 이동)
- [x] `frontend-guide-principles.md` → `senior-reference/frontend-principles.md` (이동)
- [x] `backend-guide-principles.md` → `senior-reference/backend-principles.md` (이동)
- [x] `frontend-guide-principles-ko.md` 삭제 (300/1205줄 미완성)
- [x] `backend-principles.md` 내부 참조 수정 (`frontend-guide-principles.md` → `frontend-principles.md`)
- [x] `senior-reference/README.md` 작성 (목적 + 재검토 시한 명시: 2026-08-12)

**검증 발견 사항 (계획 수정 원인)**
- 사전 추측: `frontend-guide-general.md`가 `frontend-guide.md`의 슈퍼셋 → **틀림**
- 실제: 기존 `frontend-guide.md`는 indie-specific 레시피북 (Supabase Client Setup / Auth Middleware / Stripe Checkout UI / SEO & Metadata 등 SKILL이 명시적으로 참조하는 섹션 포함), general은 일반 시니어 가이드
- 결정: 기존 정본 유지, general은 senior-reference로 격리

**Acceptance**
- `git status`에서 `knowledge/` 영역 orphan 파일 사라짐 (남은 untracked: `senior-reference/`만)
- SKILL의 `knowledge/frontend-guide.md` / `knowledge/backend-guide.md` 참조 무손상

---

## Layer 1 — Critical 버그 수정 (완료)

### L1.1 글로벌 스킬 동기화 [DONE — 2026-05-12]

**Why**
`/Users/jaykim/Documents/Projects/indie-maker/skills/`에 14개가 있지만 `~/.claude/skills/`에는 11개만 존재.
누락: `indie-architect`, `indie-copy`, `indie-monetize`.

**Done**
- [x] `bin/sync-skills.sh` 작성 (symlink 방식, idempotent)
- [x] 11개 글로벌 기존본이 프로젝트본과 완전 일치 검증 (diff -q) 후 안전하게 symlink로 대체
- [x] 14개 스킬 모두 `~/.claude/skills/indie-*` symlink 확인됨
- [x] Claude Code 세션에서 누락 3개(architect/copy/monetize) 트리거 가능 확인

**Acceptance** [DONE]
```bash
$ ls ~/.claude/skills/ | grep -c indie-
14
$ readlink ~/.claude/skills/indie-architect
/Users/jaykim/Documents/Projects/indie-maker/skills/indie-architect
```

**남은 후속 (낮음)**
- [ ] `README.md` "Getting Started"에 `bash bin/sync-skills.sh` 한 줄 추가 (멀티머신/CI 케이스)

---

### L1.2 docs/ 경로 누수 정리 [DONE — 2026-05-12]

**Why**
프레임워크 루트의 `docs/indie-planner/`, `docs/indie-market-researcher/`에 "Pulse" 프로젝트 산출물 누수.

**Done**
- [x] Pulse 산출물 4개(`pulse-spec.md` + `docs/indie-planner/*` + `docs/indie-market-researcher/*`) 모두 프레임워크 영역에서 제거됨 (외부 정리 추정)
- [x] Pulse canonical 정본 보존 확인: `local-only/project-ideas/pulse/pulse-spec.md` (326줄, Apr 30 — 제품 개요/아키텍처/데이터 모델/빌드 순서 전부 포함)
- [x] `docs/` 루트는 프레임워크 메타 전용 (`indie-sprint-playbook.md`, `senior-requirements/`)

**기록할 만한 점**
- 사라진 파일 4개의 정확한 소멸 경위 미상 — 제 명령 이력에 docs/ 건드린 적 없음
- 사라진 파일은 정본에서 파생된 보조 산출물이므로 **본질적 데이터 손실 없음** [OPINION]
- 향후 hook으로 framework `docs/`에 project 산출물 쓰이는 것을 차단해야 함 → L3.2와 연동

**Acceptance** [DONE]
- 프레임워크 루트 `docs/`에는 메타 문서만 존재 ✓

---

### L1.3 루트 클러터 정리 [DONE — 2026-05-12]

**Why**
루트에 `CHECKLIST.md`(채용과제 무관), 빈 `research/`, `.DS_Store` 잡음.

**Done**
- [x] `CHECKLIST.md` 제거됨 (외부 정리)
- [x] 빈 `research/` 폴더 제거 (rmdir)
- [x] `.DS_Store` `.gitignore`에 추가
- [x] `test-sprint/` 유지 결정 — README가 명시한 pipeline test 디렉토리

**Acceptance** [DONE]
프로젝트 루트 정돈됨:
```
CLAUDE.md, HARNESS-TODO.md, README.md, .gitignore,
bin/, docs/, knowledge/, skills/,
local-only/, projects/, test-sprint/, wrap-up/
```

---

## Layer 2 — 스프린트 상태 머신 (핵심 ROI, ~반나절)

> **핵심 통찰**: indie-maker는 "프레임워크" + "6개 프로젝트의 메타 디렉토리"의 이중 구조.
> 각 프로젝트가 독립된 sprint state를 가져야 하며, 이것이 표면화되어야 인지 부하가 감소함.

### L2.1 `.indie-sprint.json` 스키마 정의 [DONE — 2026-05-12]

**Why**
"지금 Pulse는 Day 며칠? 다음 스킬은 뭐? Kill criteria는?"이 매 세션 재구축 비용을 발생시킴.

**Done**
- [x] `schemas/indie-sprint.schema.json` 작성 (JSON Schema Draft-07)
  - 필수: `project`, `status`, `started_at`
  - 옵션: `display_name`, `stack`, `current_day` `[DERIVED]`, `current_phase` `[DERIVED]`, `completed_skills`, `next_recommended` `[DERIVED]`, `kill_criteria`, `metrics`, `launch_date`, `verdict`, `notes`
  - `additionalProperties: false` (오타 방어)
  - 모든 필드에 description (IDE IntelliSense 지원)
- [x] enum 확정:
  - `status`: `active | dormant | killed | shipped`
  - `current_phase`: 13개 phase (`idea`, `planning`, `ux`, `design`, `monetize`, `architect`, `build`, `launch-prep`, `launch`, `post-launch`, `gate`, `growth`, `retro`)
  - `verdict`: `go | watch | kill | null`
  - `completed_skills[].skill`: 14개 indie-* 스킬
- [x] `schemas/example.indie-sprint.json` — 주석된 미드-스프린트 예시
- [x] `schemas/README.md` — 사용법, IDE 통합, CLI 검증, 업데이트 절차
- [x] ajv-cli로 example → schema 검증 통과 (`schemas/example.indie-sprint.json valid`)

**핵심 설계 결정**
- **Derived vs Stored**: `current_day`, `current_phase`, `next_recommended`는 다른 필드에서 계산 가능 → `[DERIVED]` 표시. 가독성 위해 명시 저장 (hook이 동기화 유지). DRY 위반이지만 raw JSON 읽기 쉬워짐.
- **kill_criteria/metrics 자유 형식**: `additionalProperties: { ... }` — 표준 SaaS 메트릭(ph_votes/mrr/retention) 외 비표준 메트릭도 허용
- **stack 필드**: `indie-default` (Supabase+Next.js) vs 기타 — 비표준 스택은 `knowledge/senior-reference/`로 라우팅 (예: Pulse=nestjs → backend-principles.md)
- **D1=1 정책**: `current_day = (today - started_at) + 1`로 D1이 시작일. D0 아님.

**Acceptance** [DONE]
`schemas/example.indie-sprint.json` 1분 안에 읽고 sprint 상태 파악 가능.

---

### L2.1.1 프로젝트 상태 파일 작성 [DONE — 2026-05-12]

**Q1 결과**: 6개 프로젝트 모두 `dormant` 분류.

**Done**
- [x] 6개 `projects/{name}/.indie-sprint.json` 생성 (모두 status=dormant)
- [x] 파일시스템 단서로 `started_at`, `current_phase`, `completed_skills` 추정
- [x] 6개 모두 ajv 스키마 검증 통과
- [x] `projects/*`가 .gitignore 처리되어 sprint state는 per-machine 로컬 보관

**분류 결과**
| Project | current_phase | completed_skills | 비고 |
|---------|--------------|------------------|------|
| devjob-ai | planning | planner만 | 기획 후 멈춤 |
| indie-maker-web | post-launch | [] | 메타 도구, framework 외부에서 빌드 |
| jd-lens | design | researcher/planner/ux/designer | 4 phase 진행 후 멈춤 |
| my-timeline | build | planner/ux/designer | 가장 진척됨, 코드 존재 |
| pdf-annotator | idea | [] | src/만 존재 |
| pdf-viewer | build | [] | 코드 있으나 planning skip |

**기록할 만한 점**
- 활성 프로젝트가 0개 → 당장은 SessionStart hook의 효과가 제한적 ([OPINION])
- dormant도 후일 reactivate 시 historical context로 가치 있음
- indie-maker-web은 sprint product가 아닌 메타 도구 → 향후 framework "system project" 라벨 필요 가능

---

### L2.2 SessionStart hook — 상태 자동 인젝션 [DONE — 2026-05-12]

**Why**
세션 시작 시 사용자가 "어느 프로젝트, 어느 Day"인지 다시 말하는 비용 제거.

**Done**
- [x] `bin/inject-sprint-context.py` 작성 (Python3, self-contained)
  - stdin JSON에서 cwd 파싱 (Claude Code hook protocol)
  - CWD에서 위로 걸어 올라가며 `.indie-sprint.json` 탐색
  - 4가지 status 포맷: active/dormant/killed/shipped
  - active 케이스: D-day 계산 (D1=시작일), 다음 스킬 추천 (NEXT_SKILL 그래프 기반)
  - framework root: "Framework Mode" 안내
  - 그 외 경로: silent (컨텍스트 오염 없음)
  - 모든 예외 catch → exit 0 (Claude Code 권장)
- [x] `.claude/settings.json`에 SessionStart hook 등록 (matcher: "startup")
- [x] 절대경로 사용: `python3 /Users/jaykim/Documents/Projects/indie-maker/bin/inject-sprint-context.py` (단일 머신 기준)
- [x] 4가지 시나리오 수동 검증 완료:
  - dormant 프로젝트 → 상태 + resume 힌트 표시
  - framework root → framework mode 안내
  - 외부 경로 → silent
  - active 시뮬레이션 → D-day, 다음 스킬, Kill 기준 모두 정상 표시

**Acceptance** [DONE]
`cd projects/<name> && claude` 진입 시 (또는 indie-maker 루트 진입 시) 자동으로 컨텍스트 표시.
**다음 세션에서 자동 발화 확인 필요** (현 세션엔 영향 없음).

**알려진 한계 / 후속 가능**
- 절대경로 하드코딩 → 멀티머신 배포 시 수정 필요
- `.claude/` 가 .gitignore → hook 설정이 버전 관리 안 됨 (단일 머신은 OK)
- stdin JSON 파싱 실패 시 sys.argv[1] fallback — 수동 디버깅용

---

### L2.3 Statusline — 상태 상시 표시 [DONE — 2026-05-12]

**Why**
세션 중에도 Day/phase가 항상 보여야 잊지 않음.

**Done**
- [x] `bin/statusline.py` 작성 (Python3, ~95줄, 30ms 실행)
- [x] 4가지 상태 포맷 + framework mode + silent fallback
- [x] `.claude/settings.json`에 `statusLine` 등록 (프로젝트 레벨)
- [x] User-level `~/.claude/settings.json`에 statusLine 없음 확인 (충돌 없음)
- [x] 4종 시나리오 + active 시뮬레이션 통과

**포맷 샘플**
```
[my-timeline · dormant @ build]          ← dormant
[pdf-annotator · dormant @ idea]         ← dormant (이른 단계)
[indie-maker · framework]                ← framework root
[pulse D12/29 · build · MRR $12/$50]    ← active (kill 기준 진행률 표시)
[pulse D14/29 · launch-prep · paid 1/3]  ← active (mrr 없으면 paid_users로)
```

**설계 결정** [OPINION]
- **Python 선택**: 30ms로 충분, 의존성 없음, inject-sprint-context.py와 패턴 일관
- **Active 시 진행률**: kill_criteria에 `mrr_d21_usd` 또는 `paid_users_d29` 있으면 metrics와 함께 ratio 표시. 그 외는 phase만.
- **외부 경로 silent**: indie-maker 외부에선 빈 출력 → Claude 기본 statusline 표시
- **모든 예외 swallow**: statusline은 절대 crash 안 되어야 (사용자 경험)

**Acceptance** [DONE]
다음 세션부터 자동 표시. 30ms 실행 시간으로 statusline 빈번 호출에 적합.

**알려진 한계**
- 절대경로 하드코딩 (L2.2와 동일)
- `metrics.last_updated` 미체크 → 오래된 메트릭도 그대로 표시 (필요 시 stale 경고 추가)

**비용**: 45분 (실측 ~30분)

---

### L2.4 스킬 종료 시 자동 업데이트

**Why**
수동 업데이트는 잊혀짐. 스킬이 산출물을 쓰는 순간 상태도 함께 업데이트되어야 함.

**What**
- [ ] PostToolUse hook (Write 도구 대상) 추가:
  - 쓴 파일 경로가 `projects/{name}/docs/{skill}/*.md`이면
  - 해당 프로젝트의 `.indie-sprint.json` 읽고 `completed_skills`에 추가
  - `next_recommended` 자동 갱신 (스킬 의존 그래프 기반)
- [ ] 스킬 의존 그래프(`lib/skill-dependency-graph.json`) 정의:
  ```json
  {
    "indie-planner": { "next": ["indie-ux"] },
    "indie-ux": { "next": ["indie-designer"] },
    "indie-designer": { "next": ["indie-monetize", "indie-architect"] },
    ...
  }
  ```

**Acceptance**
스킬 산출물을 쓰면 `.indie-sprint.json`이 자동으로 업데이트됨 (수동 편집 0)

**비용**: 1.5시간

---

## Layer 3 — Scope & Discipline 자동화 (~3시간)

### L3.1 PreToolUse hook으로 스킬 scope 강제

**Why**
CLAUDE.md 텍스트만으로 막는 현재 방식은 새 세션/다른 컨텍스트에서 깨질 수 있음.

**What**
- [ ] PreToolUse hook(Skill 대상) 추가
- [ ] indie-maker CWD 안에서 스킬 이름이 `indie-*` 또는 `wrap-up`이 아니면 차단
- [ ] 차단 메시지: "이 프로젝트는 indie-* 스킬만 허용됩니다. 글로벌 스킬을 쓰려면 다른 디렉토리에서 작업하세요."

**Acceptance**
indie-maker CWD에서 `/rich-guide` 호출 → 차단됨
다른 디렉토리에서 동일 호출 → 정상 작동

**비용**: 45분

---

### L3.2 PostToolUse hook으로 출력 경로 검증

**Why**
스킬이 잘못된 위치에 산출물을 쓰는 사고 차단.

**What**
- [ ] Write/Edit 결과 경로 검증
- [ ] 규칙:
  - `*idea-canvas.md`, `*prd-lean.md` → `projects/{name}/docs/indie-planner/` 외부면 경고
  - `*pricing-strategy.md` → `docs/indie-monetize/` 외부면 경고
  - 프레임워크 루트 `docs/`에 프로젝트 산출물 쓰면 차단
- [ ] 차단 vs 경고 정책 결정 (초기엔 경고만 권장)

**Acceptance**
잘못된 경로에 쓰려고 하면 경고/차단 발생

**비용**: 1시간

---

### L3.3 스킬 파일 사이즈 다이어트

**Why**
14개 스킬 평균 700줄, 총 19,455줄. 한 스킬 로드 시 토큰 비용 큼.

**What**
- [ ] 각 SKILL.md에서 다음을 별도 파일로 분리:
  - Korean opening / English opening / 모든 대화 템플릿 → `dialogue.md`
  - 의사코드 / 알고리즘 / Domain Anchors → SKILL.md에 유지
- [ ] SKILL.md는 핵심 알고리즘 + `Read dialogue.md when needed` 패턴
- [ ] 측정: 다이어트 전/후 평균 줄 수 비교
- [ ] 우선순위: 1000줄 초과 3개부터 (indie-launcher 1341, indie-growth 1072, indie-ux 931)

**Acceptance**
SKILL.md 평균 < 500줄, 기능 동등성 유지

**비용**: 1.5시간 (3개 우선)

---

## Layer 4 — Speculative (보류, 재검토 조건 명시)

### L4.1 MCP 서버로 indie-maker-web 연동 [DEFER]
- indie-maker-web의 Supabase가 sprint state의 단일 진실 원천이 되는 방향
- **재검토 조건**: 활성 프로젝트 ≥ 4개이고 web 대시보드 사용 빈도 ≥ 주 3회

### L4.2 Cron으로 daily standup 자동 트리거 [DEFER]
- D1~D29 매일 같은 시간 진행 push
- **재검토 조건**: 사용자가 명시적으로 "리듬을 못 잡겠다"고 요청 시

---

## 의존성 & 권장 순서

```
L1.1 (스킬 동기화) ──┐
L1.2 (docs 누수)  ──┼── L2.1 (스키마) ── L2.2 (SessionStart) ── L2.3 (statusline)
L1.3 (클러터)     ──┘                  └── L2.4 (auto update)

L3.1 (scope) ── L3.2 (path validation) ← L2 완료 후 적용
L3.3 (다이어트) ← 독립, 언제든 가능
```

권장 시작점: **L1.1 → L1.2 → L2.1 → L2.2 → L2.3 → L2.4**
이 흐름이 끝나면 "6개 프로젝트 병렬 운영 시 인지 부하"가 즉시 감소.

---

## 산출물 체크리스트 (작업 완료 시)

- [ ] `bin/sync-skills.sh`
- [ ] `bin/inject-sprint-context.sh`
- [ ] `bin/statusline.sh`
- [ ] `bin/update-sprint-state.sh` (또는 hook 스크립트)
- [ ] `schemas/indie-sprint.schema.json`
- [ ] `lib/skill-dependency-graph.json`
- [ ] `.claude/settings.json` (hooks + statusline 설정)
- [ ] 각 `projects/{name}/.indie-sprint.json` (활성 프로젝트만)
- [ ] `README.md` 업데이트 (setup 섹션)
- [ ] `CLAUDE.md` 업데이트 (디렉토리 구조 + 하네스 동작 설명)

---

## Layer 5 — Self-Correcting & Behavior Harness + OS Readiness [신설 2026-05-12]

> **베이스**: OpenAI "Harness engineering" (2026-02) 프레임워크 → `Agent = Model + Harness`, Feedforward×Feedback × Computational×Inferential 4분면.
> **전체 계획**: `/Users/jaykim/.claude/plans/bubbly-toasting-raccoon.md`
> **목적**: indie-maker는 강한 Feedforward Inferential 외엔 발달 미흡 — 자가-수정 메커니즘과 drift 감지를 갖춰 "잘 가르치는 하네스" → "잘 가르치고 검증하는 하네스"로 진화. 동시에 오픈소스 공개 준비.

### L5.0 Portability Foundation [DONE — 2026-05-12]

**Done**
- [x] `.claude/settings.template.json` — harness 전용 템플릿 (placeholder `__INDIE_MAKER_ROOT__`)
- [x] `bin/install-harness.sh` — 멱등 설치 스크립트 (sync-skills + settings.json 머지)
  - 기존 permissions/additionalDirectories 보존, hooks와 statusLine만 갱신
  - 다른 CWD에서 호출해도 자기-위치 탐지 정상 작동 (`/tmp`에서 검증)
- [x] `.gitignore` 정교화: `.claude/*` 무시 + `!.claude/settings.template.json` 트래킹
- [x] `INSTALL.md` — clone → install → first sprint 가이드 + verification 5단계 + troubleshooting
- [x] roundtrip 검증: 기존 settings.json 보존 (한글 포함, ensure_ascii=False)

### L5.1 Lint-as-Prompt Pattern (with L3.2) [고우선, ~2h]
OpenAI 핵심 패턴 — 검증 실패 메시지에 자가-수정 명령 포함. L3.2 PostToolUse를 이 포맷으로. 우선순위 3 SKILL.md Quality Gate에 "→ If no: ..." 추가 (indie-planner, indie-ux, indie-infra). `knowledge/harness-patterns.md` 신규.

### L5.2 Framework Fitness Functions [중우선, ~1.5h]
`bin/fitness-check.py` — SKILL.md/knowledge guide/`.indie-sprint.json` 일관성 검증. pre-commit hook + GitHub Actions workflow.

### L5.3 Approved Fixtures — Behavior Regression [중우선, ~2h]
우선 3 skill에 fixture (planner/analyst/retro). `bin/run-fixtures.sh`. 기존 `test-sprint/gitMessage_2026-03-06/` 구조 통일.

### L5.4 Garbage Collection — Drift Detection [중우선, ~1.5h]
`bin/garbage-collect.py` (또는 `/indie-gc` skill) — stale dormant, stalled active, schema drift, orphan outputs 감지. 자가-수정 명령 포함 출력.

### L5.5 Cycle-Learning Constraint Injection [저우선, ~1h]
`lessons.md`에 Machine-Readable Constraints YAML 섹션 신설. indie-planner가 이를 Q5 단계의 mechanical 검증으로 변환.

### L5.6 Open-Source Packaging [후기, ~2h]
INSTALL.md, CONTRIBUTING.md, LICENSE, `examples/sample-sprint/`, README.md 갱신.

### L5.7 CI Workflow [후기, ~1h]
`.github/workflows/{fitness,schema-validate,fixtures}.yml`.

**의존성 순서**: L5.0 → (L5.1, L5.2, L5.5 병렬) → L5.3 → L5.4 → L5.6 → L5.7

---

# Track 2 — Agent Runtime Layer (M1-M5)

> **베이스**: [`docs/agent-runtime/README.md`](docs/agent-runtime/README.md) — layer 정의 + 4 컴포넌트 + 빌드 순서
> **궁극 목적**: indie-maker가 sprint 반복을 통해 *사용자에 대해* 학습하는 메타-프레임워크로 진화. 매번 다른 이유로 실패한다고 느끼지만 실제론 같은 패턴 반복인 경우를 데이터로 반증.
> **정당화 use case**: "내가 항상 어느 phase에서 막히는가?" (self-diagnosis ⭐⭐⭐⭐⭐)

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

## Milestone 3 — text-to-sql tool (~0.5d)

### M3.1 `query_portfolio` MCP tool [TODO, ~3-4h]
- [ ] LLM SQL 생성 → safety check → read-only execution
- [ ] 화이트리스트 (테이블/컬럼), timeout, row limit, SELECT-only enforcement
- [ ] SQL injection / write 시도 회귀 테스트
- **Acceptance**: 임의 자연어 → 안전한 SQL → 정확한 결과. write/DROP 시도 거부 verified
- **Depends**: M1.1, M2.1

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

## Milestone 5 — Phase 3 Parallel Build (선택, ~1d) [DEFER]

### M5.1 architecture.md 파서 [DEFER, ~2h]
### M5.2 Rex/Axel/Sam 병렬 dispatch [DEFER, ~3h]
### M5.3 Arch contract verifier [DEFER, ~2h]

**의존성 순서**: M1 → (M2 병렬 가능, 단 M2.4는 M1 후) → M3 → M4 → M5

---

# Cross-Track Dependencies

| Track 1 항목 | Track 2 항목 | 관계 |
|---|---|---|
| **T1.L2.4** PostToolUse hook | **T2.M1.3** SQLite sync hook | T2.M1.3은 T1.L2.4의 자연 확장 — 함께 진행 권장 |
| **T1.L5.5** Cycle-Learning Constraint Injection | **T2.M2.4** `get_lesson_frequency()` | T1.L5.5의 YAML constraint 가 T2.M2.4 분석 tool의 데이터 풍부도에 기여 |
| **T1.L5.2** Framework Fitness Functions | **T2.M1.1** SQLite 스키마 | T1.L5.2의 일관성 검증 범위에 SQL 스키마 포함 가능 |
| **T1.L2.1** `.indie-sprint.json` 스키마 | **T2.M1.1** SQL 스키마 | JSON ↔ SQL 매핑 — 두 스키마가 호환되어야 함 |

---

# Next Recommended Action

현재 시점 (2026-05-13) 우선순위:

1. **T2.M1.1** — Portfolio DB 스키마 정의 (block 거의 모든 T2 작업) ⭐⭐⭐⭐⭐
2. **T1.L5.1** — Lint-as-Prompt Pattern (L5 후속의 베이스) ⭐⭐⭐⭐
3. **T2.M1.2 + T1.L2.4** — Seed + sync hook 통합 진행 (cross-track 시너지) ⭐⭐⭐⭐
4. **T2.M2.1 + T2.M2.2** — indie-mcp 기본 동작 (T2.M1과 병렬 가능) ⭐⭐⭐⭐

---

## 참조

### Track 1 (Harness)
- `CLAUDE.md` — 현재 스코프 규칙
- `README.md` — 사용자 진입 흐름
- `~/.claude/plans/bubbly-toasting-raccoon.md` — L5 상세 계획 (재사용 자산, 검증 매트릭스 포함)
- [OpenAI Harness Engineering](https://openai.com/index/harness-engineering/) — 출발점 글
- [Martin Fowler: Harness Engineering for Coding Agent Users](https://martinfowler.com/articles/harness-engineering.html) — 4분면 + 3 regulation areas 구조화

### Track 2 (Agent Runtime)
- [`docs/agent-runtime/README.md`](docs/agent-runtime/README.md) — layer 정의, 4 컴포넌트, 빌드 순서, 동작 다이어그램
- `wrap-up/indie-maker-harness.md` — 의사결정 이력 (portfolio DB 결정, use case 정당화)
