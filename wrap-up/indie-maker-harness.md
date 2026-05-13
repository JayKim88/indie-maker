# Indie-Maker Harness - Wrap Up

> **Project**: `/Users/jaykim/Documents/Projects/indie-maker`
> **Scope**: `.claude/`, `bin/`, `schemas/`, `knowledge/`, `projects/*/.indie-sprint.json`, `HARNESS-TODO.md`

## Session: 2026-05-12 22:29

> **Context**: Reviewed OpenAI's harness-engineering article (2026-02) and mapped it to indie-maker — discovered framework was asymmetric (strong feedforward inferential, weak everything else); wrote a structured L5 plan; implemented L5.0 (Portability Foundation) to enable OS-public distribution.

### Done

- research: fetched and analyzed OpenAI "Harness engineering" article via WebSearch + Martin Fowler + InfoQ summaries (direct fetch of openai.com blocked 403). Synthesized the `Agent = Model + Harness` model and Feedforward×Feedback × Computational×Inferential 4-quadrant framework.
- discovery (via Explore agent): cataloged existing harness primitives in indie-maker — found Quality Gate sections in all 14 skills (not just indie-planner), 3 explicit gates (Demand Validation, Activation Validation, Monitoring Readiness), sequential read-then-validate pattern, lessons.md cycle-learning hooks in 2 skills. Updated mental model: indie-maker is mature in Feedforward Inferential and Feedback Inferential (self-attestation), weak in computational layers, zero lint-as-prompt and garbage collection.
- plan: drafted L5 implementation plan covering 7 items (~10.5h) — Portability Foundation, Lint-as-Prompt Pattern, Framework Fitness Functions, Approved Fixtures, Garbage Collection, Cycle-Learning Constraint Injection, OS Packaging, CI Workflow. Saved to `~/.claude/plans/bubbly-toasting-raccoon.md`.
- feat(harness/L5.0): added `.claude/settings.template.json` — tracked template with `__INDIE_MAKER_ROOT__` placeholder, holds harness-only config (hooks + statusLine).
- feat(bin/install-harness.sh): idempotent installer — auto-detects framework root via SCRIPT_DIR self-location, runs sync-skills, merges harness config into `.claude/settings.json` while preserving existing permissions/additionalDirectories. Verified working from `/tmp` (different CWD).
- chore(.gitignore): replaced blanket `.claude/` ignore with `.claude/*` + `!.claude/settings.template.json` allowlist. settings.json and settings.local.json remain machine-local.
- docs(INSTALL.md): clone → install → first sprint guide with 5-step verification, troubleshooting matrix, file-layout reference.
- chore(commits): commit `d76ba2d feat(harness): L5.0 — portability foundation for OS-public distribution`.
- docs(HARNESS-TODO.md): added Layer 5 section with all 7 items + sources/references; marked L5.0 DONE.

### Decisions

- **L5 as additive layer, not rewrite**: chose to keep L1-L4 in HARNESS-TODO unchanged and add L5 as a new layer (vs restructuring into OpenAI's 4-quadrant matrix). Preserves existing committed work; lowers cognitive cost for future-self reading the doc.
- **OS-public readiness as scope**: user chose this scope explicitly. Drives portability requirements (no absolute paths in tracked files), documentation depth (INSTALL.md), example expansion (deferred to L5.6), and CI (deferred to L5.7).
- **Template + idempotent installer pattern over runtime variable expansion**: avoided depending on Claude Code's variable substitution behavior (which the claude-code-guide agent confirmed lacks `$CLAUDE_PROJECT_DIR`). Template substitution at install time is explicit and works regardless of Claude Code version.
- **Non-destructive merge for settings.json**: installer preserves existing keys (permissions, additionalDirectories) and only overwrites `hooks.SessionStart` and `statusLine`. Rationale: users will accumulate their own permission entries over time; installer must not nuke them on `git pull && bin/install-harness.sh`.
- **ensure_ascii=False in installer**: avoid escaping Korean characters in settings.json when merging — preserves human-readable text.

### Issues

- **openai.com blocked WebFetch (403)**: had to triangulate the article content from Martin Fowler's commentary + InfoQ summary + Augment Code guide. Net effect minimal — Martin Fowler's framework write-up turned out to be more structured than OpenAI's original post.
- **Initial hypothesis was incomplete**: I had assumed indie-maker's harness was thin (only had SessionStart hook + statusline from L2). Explore agent revealed 14/14 skills already have Quality Gate sections — meaningful Feedback Inferential layer. Recalibrated plan to focus gaps (lint-as-prompt, fitness, garbage collection) rather than building from scratch.
- **Edit on `.gitignore` initially failed**: file not yet Read in this session. Pattern reminder: Edit requires prior Read.

### Next

- [ ] **L5.1 Lint-as-Prompt Pattern** (~2h) — extend L3.2 with self-correcting error messages; convert Quality Gates in 3 priority skills (planner/ux/infra) to include "→ If no: <fix command>" hints; write `knowledge/harness-patterns.md`
- [ ] **L5.2 Framework Fitness Functions** (~1.5h) — `bin/fitness-check.py` validating SKILL.md / knowledge guide / `.indie-sprint.json` structural consistency; pre-commit hook integration
- [ ] **L5.3 Approved Fixtures** (~2h) — fixtures for 3 priority skills (planner/analyst/retro); `bin/run-fixtures.sh`
- [ ] **L5.4 Garbage Collection** (~1.5h) — `bin/garbage-collect.py` (or `/indie-gc` skill) for stale dormant, stalled active, schema drift, orphan outputs
- [ ] **L5.5 Cycle-Learning Constraint Injection** (~1h) — machine-readable YAML constraints in lessons.md; indie-planner enforces them in Q5
- [ ] **L5.6 Open-Source Packaging** (~2h) — CONTRIBUTING.md, LICENSE, examples/sample-sprint/, README.md refresh
- [ ] **L5.7 CI Workflow** (~1h) — `.github/workflows/{fitness,schema-validate,fixtures}.yml`
- [ ] L2.4 PostToolUse hook (~1.5h, carried from previous Next) — auto-update `.indie-sprint.json` when skills write outputs
- [ ] Verify L2.2/L2.3 hooks fire in a fresh session (carried) — `cd projects/my-timeline && claude` should show DORMANT context + statusline

---

## Session: 2026-05-12 21:31

> **Context**: First harness engineering pass on indie-maker — diagnosed gaps in skill availability, docs/ path discipline, and per-project sprint state; built schema + SessionStart hook + statusline; planned remaining hooks via HARNESS-TODO.md.

### Done

- docs(HARNESS-TODO.md): created L0-L4 improvement roadmap with priority matrix, open questions, and per-layer acceptance criteria
- feat(knowledge): reorganized knowledge/ — moved 3 non-indie-stack guides to new `senior-reference/` (frontend-senior-guide.md, frontend-principles.md, backend-principles.md), deleted incomplete Korean translation (300/1205 lines), added README explaining purpose + 2026-08-12 review date
- feat(bin/sync-skills.sh): symlink-based sync script, idempotent — `ln -sfn` from `./skills/indie-*/` to `~/.claude/skills/`
- chore(skills): synced 14 skills globally (was 11/14 — `indie-architect`, `indie-copy`, `indie-monetize` were missing); verified all 11 existing globals byte-identical to project source via diff -q before symlink replacement
- chore(root): tidied root — removed empty `research/`, added `.DS_Store` to .gitignore, confirmed `test-sprint/` is intentional pipeline-test directory
- feat(schemas/indie-sprint.schema.json): JSON Schema Draft-07 for per-project sprint state
  - Required: project, status, started_at
  - Enums: status (active|dormant|killed|shipped), current_phase (13 values), verdict (go|watch|kill), skill (14 indie-* skills)
  - `[DERIVED]` markers on auto-computed fields (current_day, current_phase, next_recommended)
  - `additionalProperties: false` for typo defense
- feat(schemas/example.indie-sprint.json): annotated mid-sprint example (validates against schema via ajv)
- feat(schemas/README.md): usage guide — IDE integration, CLI validation, update procedure
- feat(projects/*/.indie-sprint.json): created 6 sprint state files for all dormant projects (devjob-ai/indie-maker-web/jd-lens/my-timeline/pdf-annotator/pdf-viewer); started_at + current_phase + completed_skills inferred from filesystem evidence; all validated via ajv
- feat(bin/inject-sprint-context.py): SessionStart hook (~150 lines, Python3, no deps)
  - Reads Claude Code hook stdin JSON for cwd
  - Walks up to find nearest `.indie-sprint.json`
  - 4 status formatters + Framework Mode + silent fallback
  - D-day computation (D1 = started_at, not D0)
  - Skill dependency graph for "next recommended"
  - All exceptions → exit 0 + stderr (silent fail per Claude Code best practice)
- feat(.claude/settings.json): registered SessionStart hook (matcher: startup)
- feat(bin/statusline.py): statusline script (~95 lines, 30ms execution)
  - 4 status formats + framework mode + silent for non-indie-maker CWD
  - Active state shows kill-criteria progress (MRR or paid users ratio)
- feat(.claude/settings.json): registered statusLine (project-level, no conflict with user-level)
- chore(commits): 2 logical commits — `chore(harness): L0+L1 — knowledge cleanup, skill sync, root tidy` (9d7d292), `feat(harness): L2.1-L2.3 — sprint state machine (schema, hook, statusline)` (d0ccb0e)

### Decisions

- **Symlink over rsync** for skill sync: edits to project source reflect instantly in `~/.claude/skills/` (no re-install). Validated byte-identity before replacement so no data loss risk. Tradeoff: doesn't work across machines via git, but user is single-machine.
- **Senior-reference folder**: non-indie-stack guides (NestJS/Apollo/RN principles) preserved separately, NOT promoted into the main knowledge/ tree. Rationale: SKILLs reference `frontend-guide.md`/`backend-guide.md` (indie stack), and validation revealed that `frontend-guide.md` contains indie-specific sections (Supabase/Stripe/SEO) that the general "senior" version did NOT have — so the general guide is NOT a superset. Preserve both, different roles.
- **Derived vs stored fields in JSON Schema**: `current_day`, `current_phase`, `next_recommended` are technically derivable but stored explicitly for raw-JSON readability. Hooks maintain sync. Accepted minor DRY violation for human ergonomics.
- **Python over Bash for hook/statusline scripts**: Python3 is always present on macOS, gives consistent JSON parsing + date math, ~30ms execution acceptable for statusline. Bash + jq would be faster but jq isn't guaranteed.
- **D1 = start day (not D0)**: `current_day = (today - started_at) + 1`. Matches indie-sprint-playbook convention.
- **All 6 projects classified dormant**: 0 active sprints currently. SessionStart hook + statusline still valuable as guardrails when user resumes any project — phase + status visible at session start without re-asking.
- **Absolute paths in `.claude/settings.json`**: Single-machine setup acceptable. Documented as a known limit for future multi-machine work.
- **`.claude/` stays gitignored**: hook configuration is per-machine; not refactoring this in scope of L2.

### Issues

- **Phantom data loss**: `pulse-spec.md` (root), `docs/indie-planner/{idea-canvas,prd-lean}.md`, `docs/indie-market-researcher/ai-product-revenue-research.md` disappeared between session start and L1.2 execution — not caused by any Bash command in this session (confirmed via mtime analysis: docs/ mtime predated the failed mv). Canonical Pulse content survives at `local-only/project-ideas/pulse/pulse-spec.md` (326 lines, Apr 30). Missing files were derivative — no substantive loss. Cause unknown (suspect IDE or prior session cleanup).
- **First Edit on `senior-reference/backend-principles.md` failed** because the file hadn't been Read first — required a Read then re-Edit. Pattern reminder: Edit needs prior Read in same session.
- **Initial mistaken hypothesis** about `frontend-guide-general.md` being a superset of `frontend-guide.md` — dependency check (grep for section references) revealed otherwise. Lesson recorded in HARNESS-TODO L0.1.

### Next

- [ ] **L2.4 PostToolUse hook** (~1.5h, High priority) — auto-update `.indie-sprint.json` when a skill writes output files; needs decision on which Write paths trigger which `completed_skills` entries; consider defining `lib/skill-dependency-graph.json` as single source of truth
- [ ] **Verify L2.2/L2.3 fire correctly** in next session — `cd projects/my-timeline && claude` should show "DORMANT" context + statusline `[my-timeline · dormant @ build]`
- [ ] **L3.1 Skill scope hook** (45min) — PreToolUse Skill matcher; block non-indie-* skills when CWD is under indie-maker; convert CLAUDE.md textual rule into enforced harness layer
- [ ] **L3.2 Output path validation hook** (1h) — PostToolUse Write/Edit matcher; warn/block when skill output paths violate `projects/{name}/docs/{skill}/` convention; would have prevented the L1.2 Pulse-leak scenario
- [ ] **L3.3 Skill file diet** (1.5h) — split dialogue templates from algorithm pseudocode in the 3 largest SKILL.md files (indie-launcher 1341, indie-growth 1072, indie-ux 931); target avg <500 lines
- [ ] **README.md update** — add `bin/sync-skills.sh` to Getting Started (deferred; needed when multi-machine use begins)
- [ ] **Reactivation trigger doc** — when a new sprint starts, set `status: active` and fill in `kill_criteria` in the project's `.indie-sprint.json`; consider a `bin/start-sprint.sh project_name` helper for L2.4 follow-up
- [ ] **L4 reassessment date 2026-08-12** — review whether senior-reference/ files are still unused (delete) or have become referenced by a project (promote)
