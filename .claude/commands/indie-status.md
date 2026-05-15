---
description: Show indie-maker sprint status across all projects (or a specific one). Shows current phase, last activity, completed skills, and the recommended next skill to invoke.
allowed-tools: Read, Bash, Glob
---

# /indie-status

Scan all indie-maker projects and report their sprint state. Use this **daily** to know where you are and what's next, without manually checking files.

## Usage

```
/indie-status                  # show all projects, sorted by recent activity
/indie-status <project-name>   # show one project in detail
/indie-status --active         # only show projects with status != "dormant" / "killed"
```

## Execution

1. **Locate sprint state files**:
   - Find all `projects/*/.indie-sprint.json` under the indie-maker root.
   - Also check the root `.indie-sprint.json` if it exists (single-project mode).

2. **Read each file** and extract:
   - `project`, `display_name`, `status`, `current_phase`, `completed_skills`, `metrics.last_updated`, `started_at`, `launch_date`

3. **Compute "days into sprint"**:
   - `today - started_at` in days (cap at D29+)

4. **Determine next recommended skill** based on `current_phase`.

   **Phase enum** (from `schemas/indie-sprint.schema.json`):
   `idea | planning | ux | design | monetize | architect | build | launch-prep | launch | post-launch | gate | growth | retro`

   | current_phase | Next recommended action |
   |---------------|------------------------|
   | `idea` (or empty) | `/indie-planner` |
   | `planning` | `/indie-ux` (or `/indie-market-researcher` if no research yet) |
   | `ux` | `/indie-designer` |
   | `design` | `/indie-monetize` |
   | `monetize` | `/indie-architect` |
   | `architect` | `/indie-backend` + `/indie-frontend` (build phase) |
   | `build` | `/indie-infra` (when ready for deploy) → then `/indie-copy` |
   | `launch-prep` | `/indie-launcher` |
   | `launch` | `/indie-analyst` (start at D21+) |
   | `post-launch` | `/indie-analyst` (continue analysis through D29) |
   | `gate` | `/indie-retro` (if Kill verdict) or `/indie-growth` (if Go verdict) |
   | `growth` | `/indie-growth` (continue experiments) |
   | `retro` | Retro complete — start a new project with `/indie-planner` |
   | **unknown value** | Print: "Phase '{value}' not in schema enum. Last completed skill: {last from completed_skills[]}. Review `.indie-sprint.json` manually." |

   **Status-based override** — regardless of `current_phase`:
   - `status: "killed"` → no next action, suggest `/indie-retro` if not yet run
   - `status: "dormant"` → flag as `💤 dormant` in status display, do not recommend next action unless user explicitly resumes

5. **Detect stalled projects**:
   - If `metrics.last_updated` is more than 7 days ago AND `status` is `"active"`, flag as `⚠️ stalled`.

6. **Render output** (all projects mode):

   ```
   📊 Indie Maker Sprint Status

   Active (3):
   ┌─────────────────────────────┬──────────────┬───────┬─────────────────────┐
   │ Project                     │ Phase        │ D#    │ Next Action         │
   ├─────────────────────────────┼──────────────┼───────┼─────────────────────┤
   │ Pulse                       │ planning ✓   │ D2    │ /indie-ux           │
   │ pdf-annotator               │ idea         │ D-    │ /indie-planner      │
   │ devjob-ai ⚠️ stalled (12d)  │ build        │ D18   │ /indie-infra        │
   └─────────────────────────────┴──────────────┴───────┴─────────────────────┘

   Dormant (3):
   - my-timeline, pdf-viewer, jd-lens

   💡 Most recent activity: Pulse (today)
   💡 Suggested focus: continue Pulse with /indie-ux
   ```

7. **Single-project mode** (`/indie-status pulse`):

   Show detailed breakdown:
   ```
   📋 Project: Pulse

   Status: active
   Started: 2026-04-30 (D2)
   Current phase: planning ✓
   Completed skills:
     - /indie-planner ✓ (idea-canvas.md, prd-lean.md)

   Kill criteria (D29):
     - PH upvotes: 50+
     - Paying customers: 1+

   Metrics:
     - last_updated: (none yet)

   ➡️ Next: /indie-ux  (UX flow + wireframes)

   📁 Artifacts:
     docs/indie-planner/idea-canvas.md
     docs/indie-planner/prd-lean.md
   ```

## Edge Cases

- **No `.indie-sprint.json` found**: print "No projects tracked. Run `/indie-planner` to start one." and exit.
- **Malformed JSON**: skip with a warning `⚠️ {file} could not be parsed`.
- **All projects dormant/killed**: print "All projects are dormant or killed. Start a new sprint with `/indie-planner`."

## Quality Rules

- **Output must be terminal-readable** (tables or aligned columns). No Markdown bullets soup.
- **Sort active projects by `last_updated` DESC** (most recent first).
- **Be specific about what to run next** — never say "do something next"; say "run `/indie-ux`".
- **Honest about stalls** — if a project hasn't moved in 7+ days, flag it. Do not silently report it as "active."

## Anti-Patterns

- ❌ Do not invoke another skill from `/indie-status`. This is read-only.
- ❌ Do not write or modify any file. Read-only.
- ❌ Do not include philosophical commentary on the sprint state — just the facts.
