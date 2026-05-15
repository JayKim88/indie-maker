---
description: Resume the most recently active indie-maker project. Auto-detects current phase, summarizes where you left off, and invokes the next recommended skill.
allowed-tools: Read, Bash, Glob, Skill, ToolSearch
---

> **Note on `Skill` tool**: The `Skill` tool may be deferred in some Claude Code configurations. If invocation fails with InputValidationError, call `ToolSearch` with `query: "select:Skill"` first to load its schema, then retry.

# /indie-resume

Continue a sprint without manually checking files. Picks up where you left off based on `.indie-sprint.json` state.

## Usage

```
/indie-resume                  # resume the most recently updated project
/indie-resume <project-name>   # resume a specific project
```

## Execution

1. **Identify target project**:
   - If argument provided → find `projects/<arg>/.indie-sprint.json`
   - Else → find the `.indie-sprint.json` with the **most recent `metrics.last_updated`** (fallback: file mtime)
   - If multiple candidates have similar timestamps (within 1h), ask the user which one

2. **Read sprint state** and summarize:

   ```
   📍 Resuming: {display_name}

   Last session: {metrics.last_updated, e.g., "2026-05-13 (yesterday)"}
   Sprint day: D{days_into_sprint}
   Current phase: {current_phase}
   Completed: {completed_skills joined by ", "}

   Last artifacts produced:
   - {most recent file under docs/indie-*/, with mtime}
   - {next most recent}
   ```

3. **Determine next skill** (same mapping as `/indie-status`):
   - Map `current_phase` → next skill (see /indie-status table)

4. **Detect blockers** before invoking:
   - If `kill_criteria` is empty and `current_phase` is past `planning` → warn: "Kill criteria not set. Run `/indie-planner` to backfill."
   - If `metrics.last_updated > 7 days ago` → ask: "This project hasn't moved in {N} days. Resume here, or pivot/kill? (continue/pivot/kill)"
   - If `status == "killed"` → refuse with: "This project is killed. Run `/indie-retro` instead, or start a new project."

5. **Confirm with user before invoking**:

   ```
   ➡️ Next recommended: {skill-name}

   Reason: {one-line — why this skill is next given current_phase + completed_skills}

   Proceed? (yes / different skill / abort)
   ```

6. **On confirmation, invoke the skill** via the `Skill` tool:
   - Pass the project path as context if the skill accepts it
   - Example: `/indie-ux ./projects/pulse/`

## Edge Cases

- **No `.indie-sprint.json` files at all**: print "No tracked projects. Run `/indie-planner` to start one." and exit.
- **Argument doesn't match any project**: print "No project named `{arg}` found. Available: {list}." and exit.
- **Current phase is the final one (`growth` or `killed`)**:
  - `growth` → suggest continuing `/indie-growth` for next experiment
  - `killed` → suggest `/indie-retro` if not yet run, else "Project closed. Start a new sprint."

## Quality Rules

- **Always summarize the last session first**, before suggesting next action. The user often needs context recall, not just a button to press.
- **Show artifacts produced**, with file paths the user can open. Mtime helps recall.
- **Ask before invoking** — never silently jump into a skill. The user might want to read prior artifacts first or pivot.
- **Respect the kill verdict** — do not resume a killed project as if it's active.

## Anti-Patterns

- ❌ Do not silently invoke the next skill without showing context — defeats the "resume" purpose
- ❌ Do not assume the user wants to continue — they may have come back to kill, pivot, or retro
- ❌ Do not skip the "what did I do last time" summary even for very recent sessions — the prompt cache might have rotated
- ❌ Do not invoke `/indie-planner` to "fix" missing kill criteria automatically — surface the gap, let the user decide

## Output Example (happy path)

```
📍 Resuming: Pulse

Last session: 2026-05-14 (today, ~2h ago)
Sprint day: D14
Current phase: planning ✓
Completed: /indie-planner

Last artifacts produced:
- docs/indie-planner/idea-canvas.md   (2h ago)
- docs/indie-planner/prd-lean.md      (2h ago)

➡️ Next recommended: /indie-ux

Reason: Planning complete with idea-canvas + prd-lean. UX phase comes next
to translate the 3 core features into user flows + wireframes.

Proceed? (yes / different skill / abort)
```
