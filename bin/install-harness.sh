#!/bin/bash
# Install / update the indie-maker harness for this clone.
#
# What it does:
#   1. Symlinks 14 indie-* skills to ~/.claude/skills/ (idempotent)
#   2. Reads .claude/settings.template.json
#   3. Substitutes __INDIE_MAKER_ROOT__ with the absolute path of this repo
#   4. Merges harness config (hooks + statusLine) into .claude/settings.json
#      — preserves any existing `permissions` and other keys
#      — overwrites/creates `hooks.SessionStart` and `statusLine` entries
#
# Re-run anytime. Safe and idempotent.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "→ indie-maker root: $ROOT"
echo

# ── Step 1: Sync skills ─────────────────────────────────────────────────────
echo "[1/2] Symlinking skills to ~/.claude/skills/..."
bash "$SCRIPT_DIR/sync-skills.sh"
echo

# ── Step 2: Generate .claude/settings.json ──────────────────────────────────
echo "[2/2] Installing hooks + statusline into .claude/settings.json..."

TEMPLATE="$ROOT/.claude/settings.template.json"
TARGET="$ROOT/.claude/settings.json"

if [ ! -f "$TEMPLATE" ]; then
    echo "ERROR: Template not found at $TEMPLATE" >&2
    exit 1
fi

mkdir -p "$ROOT/.claude"

python3 - "$TEMPLATE" "$TARGET" "$ROOT" <<'PYEOF'
import json
import sys
from pathlib import Path

template_path, target_path, root = sys.argv[1], sys.argv[2], sys.argv[3]

template = json.loads(Path(template_path).read_text())
# Drop the _comment field — it's for the template only
template.pop("_comment", None)

# Substitute placeholder in command strings
def substitute(obj):
    if isinstance(obj, dict):
        return {k: substitute(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [substitute(v) for v in obj]
    if isinstance(obj, str):
        return obj.replace("__INDIE_MAKER_ROOT__", root)
    return obj

resolved = substitute(template)

# Merge with existing target (preserve permissions, etc.)
if Path(target_path).exists():
    try:
        existing = json.loads(Path(target_path).read_text())
    except (json.JSONDecodeError, OSError):
        existing = {}
else:
    existing = {}

# Overwrite only the keys the template defines (hooks, statusLine)
for key in resolved:
    existing[key] = resolved[key]

Path(target_path).write_text(json.dumps(existing, indent=2, ensure_ascii=False) + "\n")
print(f"  -> wrote {target_path}")
print(f"  -> hooks.SessionStart: configured")
print(f"  -> statusLine: configured")
PYEOF

echo
echo "Done. Verify with:"
echo "  python3 -m json.tool $TARGET > /dev/null && echo OK"
echo
echo "Hook fires on next \`claude\` session start inside this repo."
