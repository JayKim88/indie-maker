# indie-maker Pipeline Test Runs

Each subfolder = one full pipeline test run.

## Folder naming convention

```
{projectName}_{YYYY-MM-DD}/
```

Example: `gitMessage_2026-03-06/`

If multiple runs on the same day, append sequence:
```
gitMessage_2026-03-06_1/
gitMessage_2026-03-06_2/
```

---

## Contents per run

Each run folder should contain:

| File | Source skill | Required |
|------|-------------|---------|
| `pipeline-test-report.md` | Manual | ✅ Always |
| `idea-canvas.md` | indie-planner | ✅ |
| `prd-lean.md` | indie-planner | ✅ |
| `ux-flow.md` | indie-ux | if tested |
| `wireframes.md` | indie-ux | if tested |
| `design-brief.md` | indie-designer | if tested |
| `landing-copy.md` | indie-designer | if tested |
| `launch-plan.md` | indie-launcher | if tested |
| `bip-posts.md` | indie-launcher | if tested |
| `kill-go-report.md` | indie-analyst | if tested |
| `launch-metrics.md` | indie-launcher D15 | if tested |

---

## Test runs index

| Run | Product | Date | Fixes verified | New issues found |
|-----|---------|------|---------------|-----------------|
| [gitMessage_2026-03-06](./gitMessage_2026-03-06/) | GitMessage (VS Code extension) | 2026-03-06 | 16/17 | 3 (all fixed) |
