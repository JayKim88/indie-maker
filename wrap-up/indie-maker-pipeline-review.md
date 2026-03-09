# indie-maker Pipeline Review - Wrap Up

> **Project**: `/Users/jaykim/Documents/Projects/indie-maker`
> **Scope**: `skills/`, `CLAUDE.md`, `knowledge/`, `.gitignore`

## Session: 2026-03-09 23:19

> **Context**: Added Domain Anchors to all 14 SKILL.md files (keyword + application rule pattern), ran gap analysis against 14 senior JD requirement docs, applied Critical + High gaps, then translated all 26 skill/knowledge files from Korean to English (instruction content only; Korean trigger phrases preserved).

### Done

- feat(skills/\*): added `## Domain Anchors` section to all 14 SKILL.md files — keyword + `→` application rule pattern to activate Claude's training knowledge consistently
- feat(skills/indie-market-researcher): anchors — Positioning Canvas, Demand Signal Scoring, TAM/SOM Realism, Blue Ocean Strategy, Strategic Framing Rule, AI-Critical Synthesis
- feat(skills/indie-planner): anchors — Opportunity Score, Assumption Mapping, RAT, One-line Value Prop, Founding Narrative, Kill Criteria Data Validation
- feat(skills/indie-analyst): anchors — OMTM, Retention Curve Shape, Qualitative+Quantitative cross-validation, Leading vs Lagging, Go Signal Strategy Map, No Ambiguous Verdict Rule, Root Cause Isolation
- feat(skills/indie-growth): anchors — Retention-First Rule, NSM Framework, Payback Period, Atomic Network, Revenue-Tied Experiment Framework, 14-Day Experiment Rule, Monetization Bottleneck Audit
- feat(skills/indie-retro): anchors — Pre-mortem Inversion, Survivorship Bias Warning, Assumption Autopsy, Portable Lesson Test
- feat(skills/indie-monetize): anchors — Value Metric Alignment, Decoy Effect, Van Westendorp, First Dollar Principle, AI Cost Model, Freemium Trigger Threshold
- feat(skills/indie-launcher): anchors — Launch Stacking, Warm>Cold, Social Proof Flywheel, 48-hour Rule, Launch Sequence Timing, Launch Attribution Matrix, Post-Launch Copy Velocity
- feat(skills/indie-architect): anchors — Feature Co-location, 200 LOC Rule, Single Source of Truth, Vertical Slice Architecture, ADR, AI Budget Ceiling
- feat(skills/indie-frontend): anchors — Testing Trophy, Vitest+RTL, Playwright E2E, Testing Decision Rule, Dynamic Import, Image Optimization, Bundle Analysis, Re-render Optimization, Focus Management, ARIA Attributes, Keyboard Navigation, Motion Preferences; Quality Gate expanded with 5 Should Pass + 3 Self-Assessment items
- feat(skills/indie-backend): anchors — OWASP Top 10, RLS-First Design, Idempotency Key Pattern, Rate Limiting Hierarchy, Token Budget Enforcement, Structured Logging Rule
- feat(skills/indie-infra): anchors — 12-Factor App, Defense in Depth, Observability 3 Pillars, Cost Ceiling Rule, DORA Metrics Baseline, Secrets Rotation Enforcement
- feat(skills/indie-copy): anchors — PAS/AIDA/4U/BAB, Loss Aversion, Specificity Rule, Cognitive Ease, Copy-to-Revenue Tracing, AI Copy Quality Gate
- feat(skills/indie-designer): anchors — Gestalt Principles, F/Z-Pattern, Visual Hierarchy, Hick's Law Navigation, Design Test Requirement, Design Handoff Automation
- feat(skills/indie-ux): anchors — JTBD, Fogg Behavior Model, Kano Model, Onboarding Activation Chain, User Research Before Flows, Activation Validation Gate, Wireframe Validation Metric
- docs(docs/senior-requirements/): 14 JD analysis files created (1:1 skill mapping) covering Hard Skills, Senior Differentiators, Trend Keywords — used as gap analysis source
- feat(skills/\*): applied Critical gap items from senior JD analysis across all 14 skills
- feat(skills/\*): applied High gap items (15 total) from senior JD analysis across all 14 skills
- chore(skills/\*): translated all 14 SKILL.md instruction content from Korean to English (trigger phrases kept in Korean)
- chore(knowledge/analytics-guide.md): translated final Korean section ("Nova's Analytical Limitations") to English
- chore(knowledge/\*): confirmed 11 other knowledge files already fully in English — no changes needed

### Decisions

- **Domain Anchors pattern**: keyword + source + `→` application rule (1 line per anchor). Rationale: naming a framework is weak; embedding it as a generation rule is strong — activates Claude's existing training knowledge consistently without requiring full framework extraction.
- **Gap analysis workflow**: scan senior JD requirements → compare against existing SKILL.md anchors → classify Critical/High/Low → implement Critical first, then High. Low gaps deferred.
- **Trend Keyword filtering**: only extract if (a) indie-context-scoped insight different from general knowledge, AND (b) confirmed trend — not `[SPECULATIVE]` labeled. Speculative or enterprise-only trends excluded.
- **English translation scope**: all system instructions, Domain Anchors rules, section headers → English. Korean trigger phrases (user-typed input words) and user-facing dialogue prompts → Korean preserved. Rationale: Korean UTF-8 uses 1.5-2.5x more tokens than equivalent English; English has tighter pattern matching for technical framework names.

### Next

- [ ] Run pipeline test with a standard SaaS fixture to verify Domain Anchors activate correctly in generated output
- [ ] Commit all changes (Domain Anchors + gap fills + English translation) with conventional commit messages
- [ ] Review indie-monetize SKILL.md completeness (Finn persona, pricing-strategy.md template) — carried from previous Next
- [ ] Run second pipeline test with standard web SaaS fixture (verify indie-backend P0-3 routing) — carried from previous Next

---

## Session: 2026-03-07 22:49

> **Context**: Standardized project output structure to `docs/{skill}/` paths, added indie-monetize skill (12th), expanded indie-launcher Community Channel Deep Dive, unified Glob paths across all SKILL.md files.

### Done

- feat(CLAUDE.md): updated skill count 11 → 12 (indie-monetize)
- refactor(CLAUDE.md): rewrote document flow section with `docs/{skill}/` path system
- docs(CLAUDE.md): added Project directory structure block with full docs/ subdirectory map
- feat(CLAUDE.md): added indie-monetize (Finn) to Skill Reference table and Scope allowlist
- docs(CLAUDE.md): added `knowledge/automate-guide.md` to Knowledge Documents section
- feat(skills/indie-monetize): new skill added — Finn, Phase 2-3+7, outputs `pricing-strategy.md`
- feat(skills/indie-launcher): added Step 3b Community Channel Deep Dive — standalone Reddit, HN, Discord/Slack playbooks
- fix(skills/indie-launcher): removed hardcoded BetaList subscriber count (~800) → replaced with [ESTIMATE] label
- refactor(skills/indie-market-researcher): migrated paths from `./research/` to `./docs/indie-market-researcher/`
- refactor(skills/indie-market-researcher): narrowed Glob patterns from `**/idea-canvas.md` to `./docs/indie-planner/idea-canvas.md`
- refactor(skills/indie-launcher): updated context_files Glob from `**/` to `./docs/{skill}/` explicit paths
- refactor(skills/indie-planner, ux, designer, analyst, growth, retro): aligned output paths to docs/ structure
- feat(knowledge/automate-guide.md): new knowledge doc — email drip, Stripe webhooks, metrics automation (Resend + pg_cron)
- chore(.gitignore): added `project-ideas`, `projects/*`, `.claude/`
- chore: deleted `indie-sprint-playbook.md` — content consolidated into CLAUDE.md

### Decisions

- **docs/ directory standard**: all skill outputs go to `{project}/docs/{skill-name}/` — eliminates `**/` Glob ambiguity
- **indie-monetize added**: 12th skill in the sprint, Phase 2-3 + 7, pricing-strategy.md output
- **indie-sprint-playbook.md removed**: CLAUDE.md Sprint Map + Skill Reference fully covers the content; duplicate removed
- **Community Channel Deep Dive as Step 3b**: Reddit/HN/Discord playbooks separated into a standalone section in indie-launcher — distribution coverage beyond PH

### Next

- [ ] Review indie-monetize SKILL.md completeness (Finn persona, pricing-strategy.md template)
- [ ] Review indie-launcher Step 3b Discord/Slack playbook (Reddit/HN reviewed)
- [ ] Commit all changes with conventional commit messages
- [ ] Update test-sprint/README.md index after next test run
- [ ] Run second pipeline test with standard web SaaS fixture (verify indie-backend P0-3 routing)

---

## Session: 2026-03-06 23:50

> **Context**: Full internal pipeline review — identified and fixed 17 flow issues across 8 skill files, ran full end-to-end pipeline test with a fixture product, discovered 3 additional issues and fixed them, converted all skill file content to English.

### Done

- feat: added lessons.md auto-load to indie-planner Step 0 (P0-5) — cross-sprint learning feedback loop
- feat: replaced 2-option 🔴 No Signal warn with 3-option pivot path in indie-planner (P0-1)
- feat: added Kill criteria reference benchmarks table before Q5 in indie-planner (P0-2)
- feat: added request type routing dispatch block to indie-backend for all 19 request types (P0-3)
- fix: changed Plan B failure condition from AND to OR in indie-launcher Step 9 (P0-4)
- feat: added "Expected Screen" column to prd-lean.md Core Features table template (P1-6)
- feat: added mental model validation checkpoint at end of indie-ux Step 1 (P1-7)
- feat: added UX nav/onboarding conflict detection to indie-designer Step 0 (P1-8,9)
- feat: added Activation Event question after Q5 in indie-planner + field in idea-canvas.md template (P1-10)
- feat: added monitoring readiness gate (Sentry/UptimeRobot/Analytics 3-check) to indie-infra (P1-11)
- feat: added D15 channel attribution data collection table + launch-metrics.md instruction to indie-launcher (P1-12)
- feat: added MRR diagnosis → experiment selection branching (🔴/🟡/🟢) to indie-growth Step 3.6 (P1-13)
- feat: added sub-50 user and non-PH launch edge case handling to indie-analyst Step 4 (P1-14)
- feat(test): added Monetization Model Audit (Step 3.6) to indie-growth with MON-A/B/C/D ICE experiments
- feat(test): added Niche Media Pitch section to indie-launcher Tier 3 channels
- feat: added Watch verdict branch with D43 exit criteria, re-evaluation loop, and thresholds to indie-analyst (new issue A)
- feat: added Scope Change Protocol to indie-backend, indie-frontend, and indie-infra (new issue B)
- feat: added non-SaaS stack mismatch detection (Option F) to indie-backend Step 0 (new issue C)
- chore: converted all Korean text in skill instruction blocks to English across all 9 skill files
- chore: created test-sprint/ folder with {projectName}_{YYYY-MM-DD} subfolder convention
- docs: wrote pipeline-test-report.md for GitMessage test run
- docs: created test-sprint/README.md with naming convention and runs index

### Decisions

- **Watch verdict duration**: D29 → D43 (14 days) as the standard watch period — long enough for a meaningful signal, short enough to avoid drift
- **Scope Change Protocol ownership**: Build skills (backend/frontend/infra) flag scope changes but never directly edit prd-lean.md — user always owns the document
- **English-only skill instructions**: All pseudocode, comments, and output templates in SKILL.md files are English; bilingual trigger phrases and Korean opening messages remain as-is (intentional for Korean users)
- **Test fixture naming**: `{camelCaseProjectName}_{YYYY-MM-DD}` — allows multi-run tracking and easy sorting
- **P2 items deferred**: backlog.md generation, knowledge doc explicit references, KST timezone, multi-sprint research folder structure — all deferred as non-blocking friction

### Issues

- **P0-3 not verified in test**: VS Code Extension fixture produced no DB schema questions, so indie-backend request routing dispatch was not exercised. Recommend re-running with a standard SaaS fixture to verify.
- **Skill load snapshot discrepancy**: When the Skill tool loads a SKILL.md, the content shown in conversation may lag behind file edits made in the same session (symlink points to correct file; file content is current). No action needed — runtime behavior is correct.

### Next

- [ ] Run second pipeline test with a standard web SaaS fixture to verify P0-3 (indie-backend routing dispatch)
- [ ] Update test-sprint/README.md index after each future test run
- [ ] Consider adding P2 fixes in a future session: backlog.md auto-generation, multi-sprint research folder, KST timezone note
- [ ] Commit all skill file changes to git with conventional commit messages
