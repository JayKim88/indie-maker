# Install

Setup steps for using indie-maker on a fresh clone.

---

## Prerequisites

- **Claude Code** ([install](https://docs.claude.com/en/docs/claude-code))
- **Python 3** (preinstalled on macOS; `python3 --version` to verify)
- **Bash** (preinstalled on macOS/Linux)

Optional:
- `npx` (for JSON Schema validation via `ajv-cli`)
- `git`

---

## Quick start

```bash
git clone <your-fork-of-indie-maker> ~/Documents/Projects/indie-maker
cd ~/Documents/Projects/indie-maker
bash bin/install-harness.sh
```

That's it. The installer is idempotent — re-run anytime after pulling updates.

---

## What the installer does

```
bash bin/install-harness.sh
```

1. **Symlinks 14 indie-* skills** from this repo to `~/.claude/skills/` so they become slash-commands in any Claude Code session.
2. **Generates `.claude/settings.json`** from `.claude/settings.template.json`, substituting the absolute path to this clone.
   - Registers the **SessionStart hook** (`bin/inject-sprint-context.py`) — injects sprint context on every session start
   - Registers the **statusline** (`bin/statusline.py`) — always-on per-project state display
3. **Preserves existing keys** in `.claude/settings.json` (permissions, additionalDirectories, etc.) — only `hooks.SessionStart` and `statusLine` are overwritten.

---

## Verification

After install, verify the hook fires:

```bash
# 1. Hook is registered
python3 -m json.tool .claude/settings.json | grep -A 3 SessionStart

# 2. Statusline is registered
python3 -m json.tool .claude/settings.json | grep -A 2 statusLine

# 3. 14 skills are linked globally
ls ~/.claude/skills/ | grep -c indie-     # → 14

# 4. Manually invoke the hook (simulated stdin)
echo '{"cwd": "'"$(pwd)"'"}' | python3 bin/inject-sprint-context.py
# Expected output: [Framework Mode] ...

# 5. Manually invoke the statusline
echo '{"cwd": "'"$(pwd)"'"}' | python3 bin/statusline.py
# Expected output: [indie-maker · framework]
```

If all four pass, your next `cd projects/<name> && claude` session will automatically:
- Show the sprint context block at session start
- Display project state in the statusline

---

## First sprint

```bash
# Start with research (recommended) or skip to planner if you have an idea
mkdir projects/my-first-product
cd projects/my-first-product
claude
```

In the Claude Code session:

```
/indie-market-researcher   # (optional) — D-1, desire research → 3 idea candidates
/indie-planner             # D1 — idea canvas + lean PRD + Kill criteria
/indie-ux                  # D1 PM — UX flows + wireframes
/indie-designer            # D2 — brand + landing copy
/indie-monetize            # D2-3 — pricing
/indie-architect           # D3 — architecture blueprint
# Then code with /indie-frontend, /indie-backend, /indie-infra...
```

See [README.md](README.md) for the full sprint map.

After running indie-planner once, manually create `.indie-sprint.json` at the project root (or trigger it via the [planned T1.L2.4 PostToolUse hook](ROADMAP.md)). Use [`schemas/example.indie-sprint.json`](schemas/example.indie-sprint.json) as a starting point — see [`schemas/README.md`](schemas/README.md).

---

## Updating after `git pull`

The installer is idempotent:

```bash
git pull
bash bin/install-harness.sh   # re-syncs skill symlinks + refreshes .claude/settings.json
```

Re-running is safe — it preserves your local permissions / additionalDirectories and only refreshes the harness-managed keys.

---

## Uninstalling

```bash
# Remove skill symlinks
rm ~/.claude/skills/indie-*

# Remove generated settings (keep your local overrides in settings.local.json)
rm .claude/settings.json
```

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `python3: command not found` | macOS: install via `xcode-select --install` or [python.org](https://www.python.org) |
| Skills don't appear as slash-commands after install | Restart Claude Code session; check `ls ~/.claude/skills/indie-*` |
| Hook doesn't fire on session start | Verify `.claude/settings.json` exists and contains `hooks.SessionStart`. Run `bash bin/install-harness.sh` again. |
| Statusline shows nothing in projects/ | Verify `.indie-sprint.json` exists in the project dir. Run the statusline manually (verification step 5 above). |
| `unknown format "date"` from ajv | Cosmetic — formats are advisory in ajv-cli default. Use `--strict=false` if running validation manually. |

---

## File layout

```
indie-maker/
├── bin/
│   ├── install-harness.sh          ← THIS installer
│   ├── sync-skills.sh              ← skill symlink helper
│   ├── inject-sprint-context.py    ← SessionStart hook
│   └── statusline.py               ← statusline command
├── .claude/
│   ├── settings.template.json      ← tracked — harness template with placeholder
│   ├── settings.json               ← generated, gitignored (your local config)
│   └── settings.local.json         ← gitignored (Claude-managed permissions)
├── schemas/
│   ├── indie-sprint.schema.json    ← JSON Schema for project sprint state
│   ├── example.indie-sprint.json   ← annotated sample
│   └── README.md
├── skills/indie-*/                 ← 14 sprint skills (source of truth)
├── knowledge/                      ← reference docs read by skills
├── projects/                       ← your sprint projects (gitignored)
├── ROADMAP.md                      ← unified roadmap (Track 1 harness L0–L5 + Track 2 agent-runtime M1–M5)
├── docs/agent-runtime/             ← agent runtime layer spec (Track 2 베이스)
└── CLAUDE.md                       ← project instructions for Claude
```
