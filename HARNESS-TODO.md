# Indie-Maker 하네스 개선 TODO

> **작성일**: 2026-05-12
> **베이스**: 실사용 분석 (skills 동기화 상태, docs 경로 누수, 6-프로젝트 병렬 운영)
> **목적**: 텍스트 약속에 의존하던 부분을 하네스 레이어(hooks/scripts/statusline)로 자동화하고, 부서진 부분을 수선

---

## 진행 요약

| Layer | 주제 | 작업 수 | 누적 비용 | 상태 |
|-------|------|--------|----------|------|
| L0 | knowledge 정리 (orphan 격리) | 1 | 완료 | **DONE 2026-05-12** |
| L1 | Critical 버그 수정 | 3 | ~1시간 | **DONE 2026-05-12** |
| L2 | 스프린트 상태 머신 (핵심 ROI) | 4 | ~반나절 | **3.5/4 DONE** |
| L3 | Scope & Discipline 자동화 | 3 | ~3시간 | TODO |
| L4 | Speculative (보류) | 2 | — | DEFER |

---

## 결정 필요 (Open Questions)

작업 시작 전 답이 필요한 항목:

- **Q1**: `projects/` 아래 6개 (devjob-ai, indie-maker-web, jd-lens, my-timeline, pdf-annotator, pdf-viewer) 중 현재 **활성/dormant/killed** 분류는?
  → L2 상태 머신의 enum 설계에 영향
- **Q2**: 스킬 source-of-truth는?
  - A) `/Users/jaykim/Documents/Projects/indie-maker/skills/` (14개, 현재 풀버전)
  - B) `~/.claude/skills/` (11개, 글로벌)
  → 동기화 방향 결정
- **Q3**: 첫 작업 Layer는? (L1만 / L1+L2 / L2 우선 / 다른 우선순위)
- **Q4**: docs/ 경로 정책 — "프레임워크 docs"와 "프로젝트 docs"를 어떻게 분리할 것인가?
  - 안 A: 프로젝트 docs는 `projects/{name}/docs/{skill}/` (현재 의도)
  - 안 B: 프레임워크 루트의 `docs/`는 **메타 문서 전용**, 프로젝트 산출물 금지
- ~~**Q5**: knowledge/ 신규 파일 5개 처리 방향~~ → **해결됨 (L0 참조)**

---

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

## 참조

- 분석 대화 (이번 세션)
- `CLAUDE.md` — 현재 스코프 규칙
- `README.md` — 사용자 진입 흐름
