# Indie Maker

An AI collaboration system covering every phase of the indie maker sprint —
from market research to Kill/Go decision and beyond — powered by 14 specialized interactive skills.

---

## Sprint Map

```
Path A (리서치 → 기획):
[Phase -1]   [Phase 0+1]  [Phase 1.5]  [Phase 2]   [Phase 2.5]  [Phase 2.5-3]  [Phase 3-5]     [Phase 5]       [Phase 6]  [Phase 7]    [Gate]     [Phase 8+]  [Phase 9]
 Market     →  Idea +    → UX Sprint → Design   → Monetize   → Architecture → Build +       → Launch        → Launch  → Post      → Kill/Go → Growth  → Retro
 Research     Planning               Sprint     Pricing      Blueprint      Deploy Sprint     Prep Sprint      Day       Launch
 D-1 (opt)    D1 (1 day)  D1 afternoon D2 (1 day)  D2-D3        D3 (30 min)    D3-D6 (4 days)  D7-D13 (7 days)  D14       D15-D28      D29        D30+        D29(Kill)

Path B (기획 → 수요검증 → 기획):
                [Phase 0+1]  →  validate mode  →  [Phase 0+1 continues]  → ...
                  Idea +        /indie-market-        demand-validation.md
                  Planning      researcher            auto-read by planner
                  (Q1-Q2)       --validate
```

**두 진입점 모두 indie-planner → indie-ux → indie-designer 이후 동일한 흐름으로 합류.**

**Document flow**:
```
docs/indie-market-researcher/*.md ─────────────────────────────────────────────────────────┐
                                                                                             ↓
docs/indie-planner/idea-canvas.md → docs/indie-planner/prd-lean.md
  → docs/indie-ux/ux-flow.md + wireframes.md
  → docs/indie-designer/design-brief.md + landing-copy.md
  → docs/indie-monetize/pricing-strategy.md
  → docs/indie-architect/architecture.md
  → MVP
  → docs/indie-copy/landing-copy.md + channel-posts.md + email-sequence.md
  → docs/indie-launcher/launch-plan.md + bip-posts.md + launch-metrics.md
  → docs/indie-analyst/kill-go-report.md → docs/indie-growth/growth-experiments.md + channel-strategy.md
                                         → docs/indie-retro/retrospective.md + lessons.md
docs/indie-market-researcher/demand-validation.md ┘ (기획 중 validate 실행 시)
docs/indie-retro/lessons.md → (다음 사이클 market-researcher 자동 읽기)
```

**Project directory structure** (output files saved here by default):
```
{project}/
├── docs/
│   ├── indie-market-researcher/   ← market-analysis.md, competitive-analysis.md, revenue-model-draft.md, demand-validation.md, artifacts/
│   ├── indie-planner/             ← idea-canvas.md, prd-lean.md
│   ├── indie-ux/                  ← ux-flow.md, wireframes.md
│   ├── indie-designer/            ← design-brief.md, landing-copy.md
│   ├── indie-monetize/            ← pricing-strategy.md
│   ├── indie-architect/           ← architecture.md
│   ├── indie-copy/                ← landing-copy.md, channel-posts.md, email-sequence.md
│   ├── indie-launcher/            ← launch-plan.md, bip-posts.md, launch-metrics.md
│   ├── indie-analyst/             ← kill-go-report.md
│   ├── indie-growth/              ← growth-experiments.md, channel-strategy.md
│   └── indie-retro/               ← retrospective.md, lessons.md
└── src/                           ← product code
```

---

## Skill Reference

| Skill | Agent | Trigger | Phase | Output |
|-------|-------|---------|-------|--------|
| `indie-market-researcher` | Max | `/indie-market-researcher` | -1 | `docs/indie-market-researcher/` |
| `indie-planner` | Reid | `/indie-planner` | 0+1 | `docs/indie-planner/` |
| `indie-ux` | Kai | `/indie-ux` | 1.5 | `docs/indie-ux/` |
| `indie-designer` | Vera | `/indie-designer` | 2 | `docs/indie-designer/` |
| `indie-architect` | Arch | `/indie-architect` | 2.5-3 | `docs/indie-architect/` |
| `indie-frontend` | Rex | `/indie-frontend` | 3-5 | — (guide) |
| `indie-backend` | Axel | `/indie-backend` | 3-5 | — (guide) |
| `indie-infra` | Sam | `/indie-infra` | 3-5+6 | — (guide + QA checklist) |
| `indie-monetize` | Finn | `/indie-monetize` | 2-3 + 7 | `docs/indie-monetize/` |
| `indie-copy` | Cal | `/indie-copy` | 5 | `docs/indie-copy/` |
| `indie-launcher` | Leo | `/indie-launcher` | 5 | `docs/indie-launcher/` |
| `indie-analyst` | Nova | `/indie-analyst` | 7+Gate | `docs/indie-analyst/` |
| `indie-growth` | Gio | `/indie-growth` | 8+ (Go) | `docs/indie-growth/` |
| `indie-retro` | Sage | `/indie-retro` | 9 (Kill) | `docs/indie-retro/` |

---

## Knowledge Documents

Each skill references these for best practices and code patterns.

### Core guides (default stack: Supabase + Next.js)

- `knowledge/design-guide.md` — Design system, WCAG AA, 8px grid, Atomic Design
- `knowledge/frontend-guide.md` — Next.js App Router, RSC rules, TypeScript strict, accessibility
- `knowledge/backend-guide.md` — Supabase, REST principles, OWASP Top 10, RLS
- `knowledge/infra-guide.md` — Vercel, 12-Factor App, security hardening, observability
- `knowledge/automate-guide.md` — Email drip sequences, Stripe webhooks, metrics automation (Resend + pg_cron)
- `knowledge/tech-stack.md` — Canonical stack constraints — do not deviate without reason

### Agent constitutions (extended intelligence per agent)

- `knowledge/founding-pm-guide.md` — Reid's constitution (Customer Dev + Lean + JTBD + Non-Negotiable Rules)
- `knowledge/market-intelligence-guide.md` — Max's constitution (desire-based research, demand validation)
- `knowledge/analytics-guide.md` — Nova's reference (AARRR framework, benchmarks, cohort analysis)
- `knowledge/full-stack-frontend.md` — Rex's pattern library (animation, URL state, Zustand, v0.dev)
- `knowledge/full-stack-backend.md` — Axel's pattern library (architecture trees, real-time, performance)
- `knowledge/full-stack-designer.md` — Vera's pattern library (CRO, psychology, microcopy, motion)

### Senior reference (`knowledge/senior-reference/` — NOT used by SKILLs)

These documents are preserved as senior-level reference and for non-default stacks.
**Do NOT reference them from SKILL execution.** Use them for:
- Non-default stack projects (e.g., Pulse on NestJS → `backend-principles.md`)
- Senior learning / interview prep
- Decision rationale beyond recipe-style guides

Files: `frontend-senior-guide.md`, `frontend-principles.md`, `backend-principles.md`. See `senior-reference/README.md` for reactivation criteria.

---

## Sub-agents (project-level, `.claude/agents/`)

Specialized sub-agents called BY skills to keep main context clean and enable parallel work.
Skills spawn these in parallel via the Agent tool — each runs in an isolated context window.

| Sub-agent | Called by | Purpose |
|-----------|-----------|---------|
| `competitor-researcher` | Reid (Q3), Max, Finn | Deep-dive one competitor; returns structured profile without bloating caller's context |
| `multi-channel-writer` | Cal, Leo | Generate copy for ONE channel (PH/HN/Reddit/X/email/landing); spawn in parallel for multi-channel |
| `evidence-collector` | Max, Reid, Nova | Collect raw user-voice quotes (Reddit/YouTube/G2) with source URLs — no synthesis |

**Pattern**: Caller skill builds shared brief → spawns N sub-agents in single message (parallel) → merges structured outputs.

**When NOT to use**: interview-style turns (Reid Q1-Q5), small lookups, anything that needs conversation continuity.

## Slash Commands (project-level, `.claude/commands/`)

Utility commands separate from skills. Read-only and stateless.

| Command | Purpose |
|---------|---------|
| `/indie-status` | Show sprint status across all projects; identify stalled sprints; show next recommended skill |
| `/indie-resume` | Resume the most recently active project with context summary before invoking next skill |

---

## Sprint Principles

1. **Kill criteria first** — Decide the D29 numbers before writing a line of code
2. **Pre-sale before build** — 3+ people pay → build; 0 pay → don't build
3. **Validate demand before building** — Use `indie-market-researcher --validate` if skipping full research
4. **One core flow only** — Anything outside it goes to `backlog.md`; never implement immediately
5. **Ship when it works** — Perfection is the enemy of launch
6. **Automate after $100 MRR** — manual before that, or you're optimizing too early
7. **Kill = data, not failure** — Run indie-retro to extract learning for the next sprint

---

## Skill Scope

When working inside this project, use **only the skills listed below**.
Do not invoke other globally registered skills (e.g. rich-guide, career-compass, market-pulse, portfolio-analyzer, etc.) unless explicitly requested by the user.

| Allowed Skill | Trigger |
|---------------|---------|
| `indie-market-researcher` | `/indie-market-researcher` |
| `indie-planner` | `/indie-planner` |
| `indie-ux` | `/indie-ux` |
| `indie-designer` | `/indie-designer` |
| `indie-architect` | `/indie-architect` |
| `indie-frontend` | `/indie-frontend` |
| `indie-backend` | `/indie-backend` |
| `indie-infra` | `/indie-infra` |
| `indie-monetize` | `/indie-monetize` |
| `indie-launcher` | `/indie-launcher` |
| `indie-copy` | `/indie-copy` |
| `indie-analyst` | `/indie-analyst` |
| `indie-growth` | `/indie-growth` |
| `indie-retro` | `/indie-retro` |

---

## Reference

- `indie-sprint-playbook.md` — Master sprint guide
