# Indie Maker

An AI collaboration system covering every phase of the indie maker sprint —
from market research to Kill/Go decision and beyond — powered by 11 specialized interactive skills.

---

## Sprint Map

```
Path A (리서치 → 기획):
[Phase -1]   [Phase 0+1]  [Phase 1.5]  [Phase 2]   [Phase 3-5]        [Phase 5]       [Phase 6]  [Phase 7]    [Gate]     [Phase 8+]  [Phase 9]
 Market     →  Idea +    → UX Sprint → Design   → Build +           → Launch        → Launch  → Post      → Kill/Go → Growth  → Retro
 Research     Planning               Sprint     Deploy Sprint         Prep Sprint      Day       Launch
 D-1 (opt)    D1 (1 day)  D1 afternoon D2 (1 day)  D3-D6 (4 days)     D7-D13 (7 days)  D14       D15-D28      D29        D30+        D29(Kill)

Path B (기획 → 수요검증 → 기획):
                [Phase 0+1]  →  validate mode  →  [Phase 0+1 continues]  → ...
                  Idea +        /indie-market-        demand-validation.md
                  Planning      researcher            auto-read by planner
                  (Q1-Q2)       --validate
```

**두 진입점 모두 indie-planner → indie-ux → indie-designer 이후 동일한 흐름으로 합류.**

**Document flow**:
```
research/*.md ─────────────────────────────────────────────────┐
                                                                ↓
idea-canvas.md → prd-lean.md → ux-flow.md → design-brief.md → MVP → kill-go-report.md → growth-experiments.md
                     ↑                                                                  → retrospective.md
demand-validation.md ┘ (기획 중 validate 실행 시)
                                                          lessons.md → (다음 사이클 market-researcher 자동 읽기)
```

---

## Skill Reference

| Skill | Agent | Trigger | Phase | Output |
|-------|-------|---------|-------|--------|
| `indie-market-researcher` | Max | `/indie-market-researcher` | -1 | research/*.md + idea candidates |
| `indie-planner` | Reid | `/indie-planner` | 0+1 | idea-canvas.md + prd-lean.md |
| `indie-ux` | Kai | `/indie-ux` | 1.5 | ux-flow.md + wireframes.md |
| `indie-designer` | Vera | `/indie-designer` | 2 | design-brief.md + landing-copy.md |
| `indie-frontend` | Rex | `/indie-frontend` | 3-5 | — (guide) |
| `indie-backend` | Axel | `/indie-backend` | 3-5 | — (guide) |
| `indie-infra` | Sam | `/indie-infra` | 3-5+6 | — (guide + QA checklist) |
| `indie-launcher` | Leo | `/indie-launcher` | 5 | launch-plan.md + bip-posts.md |
| `indie-analyst` | Nova | `/indie-analyst` | 7+Gate | kill-go-report.md |
| `indie-growth` | Gio | `/indie-growth` | 8+ (Go) | growth-experiments.md + channel-strategy.md |
| `indie-retro` | Sage | `/indie-retro` | 9 (Kill) | retrospective.md + lessons.md |

---

## Knowledge Documents

Each skill references these for best practices and code patterns:

- `knowledge/design-guide.md` — Design system, WCAG AA, 8px grid, Atomic Design
- `knowledge/frontend-guide.md` — Next.js App Router, RSC rules, TypeScript strict, accessibility
- `knowledge/backend-guide.md` — Supabase, REST principles, OWASP Top 10, RLS
- `knowledge/infra-guide.md` — Vercel, 12-Factor App, security hardening, observability

---

## Sprint Principles

1. **Kill criteria first** — Decide the D29 numbers before writing a line of code
2. **Validate demand before building** — Use `indie-market-researcher --validate` if skipping full research
3. **One core flow only** — Anything outside it goes to `backlog.md`; never implement immediately
4. **Ship when it works** — Perfection is the enemy of launch
5. **Kill = data, not failure** — Run indie-retro to extract learning for the next sprint

---

## Reference

- `indie-sprint-playbook.md` — Master sprint guide
