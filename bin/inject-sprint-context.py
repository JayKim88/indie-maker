#!/usr/bin/env python3
"""
SessionStart hook for indie-maker.

Injects sprint context when Claude Code starts a session inside a project
directory under projects/{name}/, or a framework-mode notice when at the
indie-maker root.

Claude Code hook protocol:
  - Receives JSON on stdin with at least `cwd` field
  - stdout text is added to Claude's session context
  - stderr is logged but not shown to Claude
  - Non-zero exit does not block the session

Silent failure: catches all exceptions, prints diagnostic to stderr, exits 0.

See HARNESS-TODO.md L2.2 and schemas/indie-sprint.schema.json.
"""

import json
import sys
from datetime import date, datetime
from pathlib import Path

SPRINT_LENGTH = 29  # D29 = Kill/Go gate

# Skill → phase mapping (fallback when current_phase is missing)
SKILL_TO_PHASE = {
    "indie-market-researcher": "research",
    "indie-planner": "planning",
    "indie-ux": "ux",
    "indie-designer": "design",
    "indie-monetize": "monetize",
    "indie-architect": "architect",
    "indie-frontend": "build",
    "indie-backend": "build",
    "indie-infra": "build",
    "indie-copy": "launch-prep",
    "indie-launcher": "launch-prep",
    "indie-analyst": "gate",
    "indie-growth": "growth",
    "indie-retro": "retro",
}

# Skill dependency graph (used for "next recommended")
NEXT_SKILL = {
    None: ["indie-market-researcher", "indie-planner"],
    "indie-market-researcher": ["indie-planner"],
    "indie-planner": ["indie-ux"],
    "indie-ux": ["indie-designer"],
    "indie-designer": ["indie-monetize", "indie-architect"],
    "indie-monetize": ["indie-architect"],
    "indie-architect": ["indie-frontend", "indie-backend", "indie-infra"],
    "indie-frontend": ["indie-backend", "indie-infra"],
    "indie-backend": ["indie-frontend", "indie-infra"],
    "indie-infra": ["indie-copy"],
    "indie-copy": ["indie-launcher"],
    "indie-launcher": ["indie-analyst"],
    "indie-analyst": ["indie-growth", "indie-retro"],
    "indie-growth": [],
    "indie-retro": [],
}


def read_stdin_cwd():
    """Parse Claude Code hook stdin JSON; return cwd or None."""
    raw = sys.stdin.read() if not sys.stdin.isatty() else ""
    if not raw.strip():
        return None
    try:
        return json.loads(raw).get("cwd")
    except (json.JSONDecodeError, ValueError):
        return None


def find_sprint_state(start: Path):
    """Walk up from start dir looking for .indie-sprint.json."""
    current = start.resolve()
    while True:
        candidate = current / ".indie-sprint.json"
        if candidate.exists():
            return candidate
        if current == current.parent:
            return None
        current = current.parent


def find_framework_root(start: Path):
    """Framework root has both skills/indie-planner/ and CLAUDE.md."""
    current = start.resolve()
    while True:
        if (current / "skills" / "indie-planner").is_dir() and (current / "CLAUDE.md").is_file():
            return current
        if current == current.parent:
            return None
        current = current.parent


def days_since(started_str: str) -> int:
    """D-day where started_at is D1."""
    started = datetime.strptime(started_str, "%Y-%m-%d").date()
    return (date.today() - started).days + 1


def fmt_active(state: dict) -> str:
    project = state.get("display_name") or state["project"]
    try:
        day = str(days_since(state["started_at"]))
    except (KeyError, ValueError):
        day = "?"

    completed = state.get("completed_skills", [])
    last_skill = completed[-1]["skill"] if completed else None
    phase = state.get("current_phase") or SKILL_TO_PHASE.get(last_skill, "idea")
    next_recs = NEXT_SKILL.get(last_skill, [])
    next_str = " or ".join("/" + s for s in next_recs) if next_recs else "(end of pipeline)"

    kill = state.get("kill_criteria") or {}
    kill_str = ", ".join(f"{k}≥{v}" for k, v in kill.items()) if kill else "not set"

    completed_short = [s["skill"].replace("indie-", "") for s in completed]
    completed_str = ", ".join(completed_short) if completed_short else "(none)"

    lines = [
        f"[Sprint Context] {project} · D{day}/D{SPRINT_LENGTH} · phase: {phase}",
        f"  Completed: {completed_str}",
        f"  Next: {next_str}",
        f"  Kill criteria: {kill_str}",
    ]
    if state.get("notes"):
        lines.append(f"  Note: {state['notes']}")
    return "\n".join(lines)


def fmt_dormant(state: dict) -> str:
    project = state.get("display_name") or state["project"]
    phase = state.get("current_phase", "?")
    return (
        f"[Sprint Context] {project} · status: DORMANT (paused at phase: {phase})\n"
        f"  To resume: set status to \"active\" in projects/{state['project']}/.indie-sprint.json"
    )


def fmt_killed(state: dict) -> str:
    project = state.get("display_name") or state["project"]
    return f"[Sprint Context] {project} · status: KILLED — see docs/indie-retro/"


def fmt_shipped(state: dict) -> str:
    project = state.get("display_name") or state["project"]
    return f"[Sprint Context] {project} · status: SHIPPED — growth phase, see docs/indie-growth/"


def fmt_framework_mode() -> str:
    return (
        "[Framework Mode] You're at the indie-maker framework root.\n"
        "  Project work belongs in projects/{name}/. Framework docs/ is meta only.\n"
        "  To start a new sprint: mkdir projects/<name> && cd $_ && claude"
    )


def main():
    cwd = read_stdin_cwd()
    if not cwd and len(sys.argv) > 1:
        cwd = sys.argv[1]
    start = Path(cwd) if cwd else Path.cwd()

    if not start.exists():
        return

    state_path = find_sprint_state(start)
    if state_path:
        try:
            state = json.loads(state_path.read_text())
        except (json.JSONDecodeError, OSError) as e:
            print(f"[Sprint Context] failed to read {state_path}: {e}", file=sys.stderr)
            return
        status = state.get("status", "active")
        formatter = {
            "active": fmt_active,
            "dormant": fmt_dormant,
            "killed": fmt_killed,
            "shipped": fmt_shipped,
        }.get(status, fmt_active)
        print(formatter(state))
        return

    framework_root = find_framework_root(start)
    if framework_root and start.resolve() == framework_root:
        print(fmt_framework_mode())


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"[Sprint Context] hook error: {exc}", file=sys.stderr)
        sys.exit(0)
