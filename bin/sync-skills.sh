#!/bin/bash
# Symlink indie-* skills from this project to ~/.claude/skills/
#
# Source of truth: ./skills/indie-*/
# After running, edits to ./skills/*/SKILL.md are reflected instantly
# in Claude Code (no re-install needed).
#
# Re-run anytime — idempotent.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_SKILLS="$(cd "$SCRIPT_DIR/../skills" && pwd)"
GLOBAL_SKILLS="$HOME/.claude/skills"

mkdir -p "$GLOBAL_SKILLS"

linked=0
for skill_dir in "$PROJECT_SKILLS"/indie-*; do
    [ -d "$skill_dir" ] || continue
    skill_name=$(basename "$skill_dir")
    target="$GLOBAL_SKILLS/$skill_name"

    rm -rf "$target"
    ln -s "$skill_dir" "$target"
    echo "  -> $skill_name"
    linked=$((linked + 1))
done

echo
echo "Linked $linked skills to $GLOBAL_SKILLS/"
