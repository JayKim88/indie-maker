# indie-maker Pipeline Review - Wrap Up

> **Project**: `/Users/jaykim/Documents/Projects/indie-maker`
> **Scope**: `skills/` (11 skill files), `test-sprint/`

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
