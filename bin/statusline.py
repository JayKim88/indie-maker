#!/usr/bin/env python3
"""
Statusline for indie-maker.

Output: single compact line showing the current project's sprint state,
or [indie-maker · framework] at framework root, or empty when not in
indie-maker context.

Reads Claude Code statusline stdin JSON for `cwd`. Designed to be fast
(no external deps, never crashes — silent failure).
"""

import json
import sys
from datetime import date, datetime
from pathlib import Path

SPRINT_LENGTH = 29


def read_stdin_cwd():
    raw = sys.stdin.read() if not sys.stdin.isatty() else ""
    if not raw.strip():
        return None
    try:
        return json.loads(raw).get("cwd")
    except (json.JSONDecodeError, ValueError):
        return None


def find_sprint_state(start: Path):
    current = start.resolve()
    while True:
        candidate = current / ".indie-sprint.json"
        if candidate.exists():
            return candidate
        if current == current.parent:
            return None
        current = current.parent


def find_framework_root(start: Path):
    current = start.resolve()
    while True:
        if (current / "skills" / "indie-planner").is_dir() and (current / "CLAUDE.md").is_file():
            return current
        if current == current.parent:
            return None
        current = current.parent


def days_since(started: str) -> int:
    d = datetime.strptime(started, "%Y-%m-%d").date()
    return (date.today() - d).days + 1


def format_active(state: dict) -> str:
    project = state.get("project", "?")
    phase = state.get("current_phase") or "?"
    try:
        day = days_since(state["started_at"])
        day_str = f"D{day}/{SPRINT_LENGTH}"
    except (KeyError, ValueError):
        day_str = "D?"

    # Show MRR progress if both kill threshold and current metric are set
    kill = state.get("kill_criteria") or {}
    metrics = state.get("metrics") or {}
    mrr_str = ""
    if "mrr_d21_usd" in kill and metrics.get("mrr_usd") is not None:
        mrr_str = f" · MRR ${metrics['mrr_usd']}/${kill['mrr_d21_usd']}"
    elif "paid_users_d29" in kill and metrics.get("paid_users") is not None:
        mrr_str = f" · paid {metrics['paid_users']}/{kill['paid_users_d29']}"

    return f"[{project} {day_str} · {phase}{mrr_str}]"


def main():
    cwd = read_stdin_cwd()
    start = Path(cwd) if cwd else Path.cwd()

    if not start.exists():
        return

    state_path = find_sprint_state(start)
    if state_path:
        try:
            state = json.loads(state_path.read_text())
        except (json.JSONDecodeError, OSError):
            return

        project = state.get("project", "?")
        status = state.get("status", "active")
        phase = state.get("current_phase") or "?"

        if status == "active":
            print(format_active(state))
        elif status == "dormant":
            print(f"[{project} · dormant @ {phase}]")
        elif status == "killed":
            print(f"[{project} · killed]")
        elif status == "shipped":
            print(f"[{project} · shipped]")
        return

    framework_root = find_framework_root(start)
    if framework_root and start.resolve() == framework_root:
        print("[indie-maker · framework]")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # never crash statusline
