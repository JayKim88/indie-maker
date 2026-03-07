# JD Lens - Wrap Up

> **Project**: `/Users/jaykim/Documents/Projects/indie-maker`
> **Scope**: `projects/jd-lens/`

## Session: 2026-03-07 22:01

> **Context**: Completed indie-ux (UX flow + wireframes) → indie-designer (design system + landing copy) → indie-backend (DB schema + API design).

### Done

- feat: UX design completed (indie-ux / Kai)
  - Mental model: LinkedIn + Notion + GitHub → left sidebar pattern
  - All task flows confirmed ≤3 steps
  - Screen inventory finalized: 7 screens (including Extension popup)
  - Activation design: blank state → "Install Extension" CTA → 3 JDs → skill insights
  - Saved `docs/indie-ux/ux-flow.md`
  - Saved `docs/indie-ux/wireframes.md` (5 core screens + interaction states)
- feat: Design system finalized (indie-designer / Vera)
  - Brand: Trust/Professional + clarity → blue-600 (#2563EB, 5.2:1 WCAG AA)
  - Font: Inter single family
  - shadcn/ui component list finalized (chart, sidebar, sheet included)
  - Saved `docs/indie-designer/design-brief.md`
  - Saved `docs/indie-designer/landing-copy.md`
- feat: DB schema + API design completed (indie-backend / Axel)
  - Tables: profiles, subscriptions, jd_entries, jd_skills
  - jd_entries + jd_skills separated (optimized for SQL GROUP BY aggregation)
  - RLS enabled on all tables
  - APIs: POST /api/jds, GET /api/jds, GET /api/skills
  - Claude API skill extraction service (jd-parser.ts) designed
  - Extension → server auth pattern confirmed (chrome.storage.local + Supabase JWT)
  - Free tier limit enforced server-side (prevents client-side bypass)

### Decisions

- **jd_entries + jd_skills as separate tables**: Better than JSONB for SQL aggregation — GROUP BY skill_name for frequency ranking
- **Claude Haiku for parsing**: Opus/Sonnet not needed for JD parsing — Haiku is faster and cheaper
- **Background parsing**: Fire-and-forget Claude API call after JD save response → no user-facing latency
- **Extension auth**: Use chrome.storage.local as Supabase Auth storage → persistent session
- **blue-600 as single primary**: No secondary accent — reflects "clarity" brand direction

### Issues

- **No GROUP BY in Supabase JS SDK**: Aggregation must be done in JS (only a performance concern at thousands+ records)
- **No retry on parse failure**: Fire-and-forget means Claude API failures leave `is_parsed=false` — retry queue needed in V2

### Next

- [ ] Design landing page smoke test (measure paid conversion from first 5 free JDs over 2 weeks)
- [ ] Clean up empty `research/` folder in project root
- [ ] `/indie-frontend` — Chrome Extension MV3 content script + popup implementation
- [ ] `/indie-frontend` — Next.js dashboard (skill bar chart) + /jds page
- [ ] Create Supabase project + write migration files
- [ ] Create Stripe product/price + implement webhook
- [ ] `/indie-infra` — Vercel deployment + domain setup

---

## Session: 2026-03-07 17:07

> **Context**: JD Lens demand validation → confirmed Chrome Extension approach → indie-planner session completed (idea-canvas + prd-lean saved).

### Done

- feat: JD Lens demand validation completed (indie-market-researcher --validate)
  - Demand Score 7/10, WTP Score 6/10 → Validated
  - Key gap identified: all existing tools are "1 JD vs 1 resume" — multi-JD aggregation unexplored
  - Saved `research/demand-validation.md`
- feat: Chrome Extension technical approach confirmed
  - Client-side DOM parsing adopted (handles platforms like LinkedIn)
  - Fallback order: DOM parsing → text paste (screenshot OCR deferred to V2)
  - Server-side crawling excluded (platform ToS risk)
- feat: indie-planner session completed (Reid)
  - Product name: JD Lens
  - Kill criteria: at least 1 paid conversion by D29
  - Activation event: view common skill frequency ranking after adding 3 JDs
  - Business model: Freemium (Free 5 JDs / Pro $9/mo KR · $15/mo Global)
  - Saved `idea-canvas.md`
  - Saved `prd-lean.md`
- chore: Project file structure organized
  - Created `projects/jd-lens/` folder
  - Moved idea-canvas.md, prd-lean.md, research/demand-validation.md

### Decisions

- **Chrome Extension MV3 client-side parsing**: Content script parses DOM in user's browser context → no LinkedIn ToS issues
- **Screenshot OCR deferred to V2**: DOM parsing + text paste fallback is sufficient for MVP. OCR cost model to be evaluated later
- **Freemium with 5-JD free tier**: Activation event (3 JDs) falls within free tier — users experience value before hitting paywall
- **Minimal kill criteria (1 paid conversion)**: Low threshold for fast judgment in early validation stage
- **Tech stack**: Next.js 15 + Supabase + Stripe + Vercel + Chrome MV3 + Claude API (JD parsing)

### Issues

- **ChatGPT as free alternative is the biggest threat**: "Paste multiple JDs + analyze" already possible with ChatGPT. Differentiation must come from saved history, automation, and UX
- **Per-platform DOM selector maintenance**: LinkedIn/Wanted/Saramin structure changes require selector updates — ongoing maintenance cost
- **Korean WTP unvalidated**: $8–15/mo estimated but actual willingness-to-pay from Korean job seekers needs smoke test

### Next

- [x] Run `/indie-ux` — Extension popup + dashboard UX flow + wireframes (from previous Next)
- [ ] Design landing page smoke test (measure paid conversion from first 5 free JDs over 2 weeks)
- [x] Chrome Extension MV3 technical review (pre-check major platform selectors + fallback strategy) (from previous Next)
- [x] Run `/indie-designer` (from previous Next)
- [ ] Clean up empty `research/` folder in project root
