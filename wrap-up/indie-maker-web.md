# indie-maker Web - Wrap Up

> **Project**: `/Users/jaykim/Documents/Projects/indie-maker`
> **Scope**: `indie-maker-web/` (Next.js SaaS), `skills/` (MCP integration), `~/.claude/settings.json`

## Session: 2026-03-07 21:19

> **Context**: Converted indie-maker CLI framework into a SaaS web service, and built the full pipeline for auto-connecting Claude Code skills with the web app via an MCP server.

### Done

- feat(web): Built Next.js 14 App Router + Supabase + shadcn/ui SaaS web app (`indie-maker-web/`)
- feat(web): Designed and migrated DB schema (projects, documents, task_completions, metrics + RLS)
- feat(web): GitHub OAuth auth + middleware redirects (login/protected routes)
- feat(web): `/dashboard` project list, `/projects/new` creation form
- feat(web): `/today` daily task checklist (D1–D29 static tasks + completion persistence)
- feat(web): `/timeline` D1–D29 timeline grid (phase colors, completion rate display)
- feat(web): `/documents` document hub (markdown upload/view/preview)
- feat(web): `/metrics` KPI tracker + Kill/Go gauge (recharts)
- fix(web): `useOptimistic` React 19 error → replaced with `useState`
- fix(web): Supabase generic type inference error → explicit `as Type` casting
- fix(web): Login page SSR build error → `dynamic = 'force-dynamic'`
- feat(mcp): Implemented indie-maker MCP server (`mcp-server/src/index.ts`)
  - `im_get_status` — fetch current Day / completed tasks / KPIs
  - `im_complete_task` — mark a task as completed
  - `im_upload_document` — upload/update a document to the hub
  - `im_log_metric` — record a KPI metric
- feat(mcp): Project identification supports both UUID and name (DB ilike search)
- feat(mcp): Registered MCP server globally in `~/.claude/settings.json`
- feat(skills): Added MCP auto-call instructions to 6 skill SKILL.md files
  (indie-planner, indie-market-researcher, indie-ux, indie-designer, indie-launcher, indie-analyst)
- refactor(mcp): Switched project identification from hardcoded UUID to `.indie-maker` file-based approach
  (supports different projects per session — place `.indie-maker` in each project root)

### Decisions

- **MCP transport**: stdio (Claude Code CLI standard)
- **Project identification**: Store project name in `.indie-maker` file at project root → look up UUID by name on each MCP call. `settings.json` env var is fallback only (empty by default)
- **AI skill location**: Skills continue to run in Claude Code CLI. Web app manages outputs only
- **MCP integration scope**: Core 6 skills only (planner/researcher/ux/designer/launcher/analyst). Build/infra skills excluded (no document outputs)
- **VSCode Extension not supported**: `settings.json` MCP only works in Claude Code CLI. VSCode Extension users must switch to CLI

### Issues

- **MCP not available in VSCode Extension**: `im_*` tools do not load in VSCode Extension sessions — CLI only
- **Empty string handling**: `??` operator passes empty strings through → replaced with `||` to ignore empty env vars

### Next

- [ ] Create `.indie-maker` file in jd-analyzer project root: `echo "jd-analyzer" > .indie-maker`
- [ ] End-to-end test from CLI: `cd jd-analyzer && claude` → run `/indie-planner` → verify web app
- [ ] Create a second project to validate multi-project isolation
- [ ] Implement indie-maker-web landing page (`/` root)
- [ ] Integrate Stripe Checkout (Free/Pro/Lifetime plans)
- [ ] Deploy indie-maker-web to production (Vercel)
- [ ] Commit MCP server changes (`indie-maker-web` repo)
